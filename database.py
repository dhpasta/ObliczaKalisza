import pymysql
import pymysql.cursors
import datetime
from time import time
import os

from connect import *
import variables as var
from coordinates import *

class Database:
    def connect(self):
        return connect_params(self)


    def get_final_results_24(self):
        con = Database.connect(self)
        cursor = con.cursor(pymysql.cursors.DictCursor)

        data_hard = {}
        cursor.execute("SELECT * FROM final_results_24 WHERE path='hard' order by points desc, time asc;")
        data_hard = cursor.fetchall()

        data_easy = {}
        cursor.execute("SELECT * FROM final_results_24 WHERE path='easy' order by points desc, time asc;")
        data_easy = cursor.fetchall()

        con.close()

        return data_easy, data_hard


    def register_patrol(self):
        con = Database.connect(self)
        cursor = con.cursor()

        cursor.execute("SELECT patrol_name FROM patrols WHERE path='easy' AND fraction IS NULL ORDER BY patrol_name;")
        easy_path = cursor.fetchall()

        cursor.execute("SELECT patrol_name FROM patrols WHERE path='hard' AND fraction IS NULL ORDER BY patrol_name;")
        hard_path = cursor.fetchall()

        con.close()

        return easy_path, hard_path


    def set_patrol_id(self, form):
        con = Database.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute("SELECT phone FROM patrols WHERE patrol_name=%s", form['patrol_name'])
            phone = cursor.fetchone()[0]
            if form['code'] == phone[-3:]:
                cursor.execute("UPDATE patrols SET fraction=%s WHERE patrol_name='%s';" % (form['fraction'], form['patrol_name']))

                cursor.execute("SELECT id FROM patrols WHERE patrol_name=%s", form['patrol_name'])
                patrol_id = cursor.fetchone()[0]
            else:
                patrol_id = None

            con.commit()

            return patrol_id
        except:
            con.rollback()

            raise
        finally:
            con.close()


    def patrol_data(self, patrol_id):
        con = Database.connect(self)
        cursor = con.cursor()

        patrol_data = {}

        patrol_data['id'] = patrol_id
        
        cursor.execute("SELECT patrol_name FROM patrols WHERE id=%s;" % patrol_id)
        patrol_data['name'] = cursor.fetchone()[0]

        cursor.execute("SELECT path FROM patrols WHERE id=%s;" % patrol_id)
        patrol_data['path'] = cursor.fetchone()[0]

        cursor.execute("SELECT fraction FROM patrols WHERE id=%s;" % patrol_id)
        patrol_data['fraction'] = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(points),0) AS SUM FROM logs WHERE patrol_id=%s" % patrol_id)
        patrol_data['points'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM logs WHERE patrol_id='%s' AND point_type='gold'" % (patrol_id))
        patrol_data['hints'] = cursor.fetchone()[0]
        if patrol_data['hints'] > 0:
            if patrol_data['path'] == 'hard': patrol_data['hints'] = patrol_data['hints'] + 12
            cursor.execute("SELECT url, insignum FROM hints WHERE id=%s" % patrol_data['hints'])
            patrol_data['hint_img'] = cursor.fetchone()
            if patrol_data['path'] == 'hard': patrol_data['hints'] = patrol_data['hints'] - 12

        cursor.execute("SELECT COALESCE(SUM(points),0) AS SUM FROM logs WHERE patrol_id=%s AND point_type='character'", patrol_id)
        patrol_data['stamps'] = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM logs WHERE point_type='bonus' AND patrol_id=%s", patrol_id)
        patrol_data['bonus'] = cursor.fetchone()[0]

        cursor.execute("SELECT EXISTS(SELECT patrol_id FROM logs WHERE patrol_id=%s AND point_type='insignia' AND point_id=1);" % patrol_id)
        patrol_data['scepter'] = cursor.fetchone()[0]

        cursor.execute("SELECT EXISTS(SELECT patrol_id FROM logs WHERE patrol_id=%s AND point_type='insignia' AND point_id=2);" % patrol_id)
        patrol_data['apple'] = cursor.fetchone()[0]

        cursor.execute("SELECT EXISTS(SELECT patrol_id FROM logs WHERE patrol_id=%s AND point_type='insignia' AND point_id=3);" % patrol_id)
        patrol_data['sword'] = cursor.fetchone()[0]

        cursor.execute("SELECT EXISTS(SELECT patrol_id FROM logs WHERE patrol_id=%s AND point_type='coronation');" % patrol_id)
        patrol_data['coronation'] = cursor.fetchone()[0]

        con.close()
        return patrol_data


    def qr_data(self, id):
        con = Database.connect(self)
        cursor = con.cursor()
        
        cursor.execute("SELECT EXISTS(SELECT id FROM qr WHERE id='%s');" % id)
        check = cursor.fetchone()[0]
        

        if check:
            data = {}
            
            cursor.execute("SELECT type FROM qr WHERE id='%s'" % id)
            data['type'] = cursor.fetchone()[0]

            cursor.execute("SELECT district FROM qr WHERE id='%s'" % id)
            data['district'] = cursor.fetchone()[0]

            con.close()
            return data
        else:
            con.close()
            return False


    def qr_patrol(self, qr_id, patrol_id):
        con = Database.connect(self)
        cursor = con.cursor()

        data = Database.qr_data(self, qr_id)

        cursor.execute("SELECT fraction FROM patrols WHERE id=%s", patrol_id)
        patrol_fraction = cursor.fetchone()[0]

        if not data:
            return "failure", False


        if data['type'] == 'silver':
            cursor.execute("SELECT fraction FROM districts WHERE log_type='occupation' AND id='%s'" % (data['district']))
            occupation = cursor.fetchone()[0]

            cursor.execute("SELECT fraction FROM districts WHERE log_type='privilege' AND id='%s'" % (data['district']))
            privilege = cursor.fetchone()[0]

            if occupation == 0:
                cursor.execute("SELECT EXISTS(SELECT point_id FROM logs WHERE point_id='%s' AND fraction=%s)" % (qr_id, patrol_fraction))
                check = cursor.fetchone()[0]
                if check:
                    con.close()
                    return "collected", data['type']
                else:
                    cursor.execute("INSERT INTO logs (patrol_id, fraction, point_type, point_id, district, points, timestamp) VALUES (%s, %s, '%s', '%s', %s, %s, '%s');" % (patrol_id, patrol_fraction, data['type'], qr_id, data['district'], var.points_silver_qr, datetime.datetime.now().time().strftime("%H:%M:%S")))
                    con.commit()
                    cursor.execute("SELECT COUNT(*) FROM logs WHERE point_type='silver' AND fraction=%s AND district=%s" % (patrol_fraction, data['district']))
                    advance = cursor.fetchone()[0]
                    
                    if privilege == patrol_fraction:
                        required = 7
                    else:
                        required = 10
                    
                    if advance < required:
                        con.close()
                        Database.generate_map(self)
                        return "find", data['type']
                    else:
                        cursor.execute("UPDATE districts SET fraction=%s WHERE log_type='occupation' AND id=%d" % (patrol_fraction, data['district']))
                        con.commit()
                        con.close()
                        Database.generate_map(self)
                        return "takeover", data['type']
            else:
                con.close()
                return "occupied", data['type']


        if data['type'] == 'gold':
            cursor.execute("SELECT EXISTS(SELECT point_id FROM logs WHERE point_id='%s' AND patrol_id=%s)" % (qr_id, patrol_id))
            check = cursor.fetchone()[0]
            if check:
                con.close()
                return False, data['type']
            else:
                try:

                    cursor.execute("INSERT INTO logs (patrol_id, fraction, point_type, point_id, district, points, timestamp) VALUES (%s, %s, '%s', '%s', %s, %s, '%s');" % (patrol_id, patrol_fraction, data['type'], qr_id, data['district'], var.points_gold_qr, datetime.datetime.now().time().strftime("%H:%M:%S")))
                    con.commit()
                    print("check 8")
                    
                    return True, data['type']
                except:
                    con.rollback()

                    raise
                finally:
                    con.close()


    def get_hint(self, patrol_id):
        con = Database.connect(self)
        cursor = con.cursor()

        cursor.execute("SELECT COUNT(*) FROM logs WHERE patrol_id='%s' AND point_type='gold'" % (patrol_id))
        check = cursor.fetchone()[0]

        if check <= 12:
            con.close()
            return True
        else:
            con.close()
            return False


    def characters_list(self):
        con = Database.connect(self)
        cursor = con.cursor()

        cursor.execute("SELECT id, name FROM characters;")
        data = cursor.fetchall()

        con.close()

        return data


    def character_data(self, character_id):
        con = Database.connect(self)
        cursor = con.cursor(pymysql.cursors.DictCursor)

        data = {}

        cursor.execute("SELECT name FROM characters WHERE id=%s;" % character_id)
        data['character_name'] = cursor.fetchone()

        cursor.execute("SELECT p.patrol_name, l.points, l.timestamp FROM logs as l INNER JOIN patrols AS p ON l.patrol_id=p.id WHERE l.point_type='character' AND l.point_id=%s ORDER BY timestamp DESC", character_id)
        data['visited'] = cursor.fetchall()

        cursor.execute("SELECT patrol_name from patrols AS p WHERE fraction IS NOT NULL AND p.patrol_name NOT IN (SELECT p.patrol_name FROM logs as l INNER JOIN patrols AS p ON l.patrol_id=p.id WHERE l.point_type='character' AND l.point_id=%s);", character_id)
        data['remaining'] = cursor.fetchall()

        con.close()

        return data


    def character_patrol_check(self, patrol_id, character_id):
        con = Database.connect(self)
        cursor = con.cursor()

        cursor.execute("SELECT EXISTS(SELECT patrol_id FROM logs WHERE point_type='character' AND patrol_id=%s AND point_id=%s)" % (patrol_id, character_id))
        check = cursor.fetchone()[0]
        
        if check == 0:
            cursor.execute("SELECT fraction FROM patrols WHERE id=%s" % (patrol_id))
            fraction = cursor.fetchone()[0]
            
            district = character_id

            cursor.execute("SELECT fraction FROM districts WHERE log_type='occupation' AND id=%s" % (district))
            occupation = cursor.fetchone()[0]

            if occupation == fraction:
                con.close()
                return "occupant"
            else:
                con.close()
                return "normal"
        else:
            con.close()
            return "already_visited"


    def character_grant_points(self, request):
        con = Database.connect(self)
        cursor = con.cursor()

        try:
            points = int(request.form['points'])

            cursor.execute("SELECT EXISTS(SELECT patrol_id FROM logs WHERE point_type='character' AND patrol_id=%s AND point_id=%s)" % (request.form['patrol_id'], request.form['character_id']))
            check = cursor.fetchone()[0]

            if check != 0:
                return False
            else:
                cursor.execute("SELECT fraction FROM patrols WHERE id=%s" % (request.form['patrol_id']))
                fraction = cursor.fetchone()[0]

                if request.form['district_owner'] == 'occupant':
                    cursor.execute("INSERT INTO logs (patrol_id, fraction, point_type, point_id, points, timestamp) VALUES (%s, %s, 'bonus', %s, %s, '%s');" % (request.form['patrol_id'], fraction, request.form['character_id'], 3, datetime.datetime.now().time().strftime("%H:%M:%S")))

                cursor.execute("INSERT INTO logs (patrol_id, fraction, point_type, point_id, points, timestamp) VALUES (%s, %s, 'character', %s, %s, '%s');" % (request.form['patrol_id'], fraction, request.form['character_id'], points, datetime.datetime.now().time().strftime("%H:%M:%S")))
                con.commit()

                return True
        except:
            con.rollback()

            raise
        finally:
            con.close()

    def insignia(self, patrol_id, insignia_id):
        con = Database.connect(self)
        cursor = con.cursor()

        cursor.execute("SELECT EXISTS(SELECT patrol_id FROM logs WHERE point_type='insignia' AND patrol_id=%s AND point_id=%s)" % (patrol_id, insignia_id))
        check = cursor.fetchone()[0]

        if check == 0:
            try:
                cursor.execute("SELECT fraction FROM patrols WHERE id=%s" % (patrol_id))
                fraction = cursor.fetchone()[0]

                cursor.execute("INSERT INTO logs (patrol_id, fraction, point_type, point_id, points, timestamp) VALUES (%s, %s, 'insignia', %s, 10, '%s');" % (patrol_id, fraction, insignia_id, datetime.datetime.now().time().strftime("%H:%M:%S")))
                con.commit()

                return True
            except:
                con.rollback()

                raise
            finally:
                con.close()
        else:
            con.close()
            return False


    def coronation(self, patrol_id):
        con = Database.connect(self)
        cursor = con.cursor()

        cursor.execute("SELECT EXISTS(SELECT patrol_id FROM logs WHERE point_type='coronation' AND patrol_id=%s)" % (patrol_id))
        check = cursor.fetchone()[0]

        if check == 0:
            try:
                cursor.execute("SELECT path FROM patrols WHERE id=%s" % (patrol_id))
                path = cursor.fetchone()[0]

                cursor.execute("SELECT fraction FROM patrols WHERE id=%s" % (patrol_id))
                fraction = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM districts WHERE log_type='occupation' AND fraction=%s" % (fraction))
                occupation = cursor.fetchone()[0]

                cursor.execute("SELECT COALESCE(SUM(points),0) AS SUM FROM logs WHERE patrol_id=%s AND point_type='character'", patrol_id)
                stamps = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM logs WHERE point_type='bonus' AND patrol_id=%s", patrol_id)
                bonus = cursor.fetchone()[0]

                stamps = stamps + bonus

                cursor.execute("SELECT COUNT(*) FROM logs WHERE point_type='insignia' AND patrol_id=%s" % (patrol_id))
                insignia = cursor.fetchone()[0]

                if path == 'easy' and occupation >= 1 and stamps >= 15 and insignia == 3:
                    cursor.execute("INSERT INTO logs (patrol_id, fraction, point_type, point_id, points, timestamp) VALUES (%s, %s, 'coronation', 0, 20, '%s');" % (patrol_id, fraction, datetime.datetime.now().time().strftime("%H:%M:%S")))
                    con.commit()
                    return "success"

                if path == 'hard' and occupation >= 2 and stamps >= 20 and insignia == 3:
                    cursor.execute("INSERT INTO logs (patrol_id, fraction, point_type, point_id, points, timestamp) VALUES (%s, %s, 'coronation', 0, 20, '%s');" % (patrol_id, fraction, datetime.datetime.now().time().strftime("%H:%M:%S")))
                    con.commit()
                    return "success"

                return "unsatisfactorily"
            except:
                con.rollback()

                raise
            finally:
                con.close()
        else:
            con.close()
            return "already_corronated"
            



    def time_stop(self, patrol_id):
        con = Database.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute("UPDATE patrols SET time='%s' WHERE id=%s" % (datetime.datetime.now().strftime("%H:%M:%S"), patrol_id))
            con.commit()

            return True
        except:
            con.rollback()

            raise
        finally:
            con.close()


    def register_qr(self, form):
        con = Database.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute("SELECT EXISTS(SELECT id FROM qr WHERE id='%s');" % form['qr_id'])
            check = cursor.fetchone()[0]

            if check:
                return "exists"
            
            cursor.execute("SELECT COUNT(*) FROM qr WHERE type='%s' AND district=%s" % (form['type'], form['district']))
            district = cursor.fetchone()[0]

            if form['type'] == 'silver': qr_max = 12
            if form['type'] == 'gold': qr_max = 3

            if district < qr_max:
                cursor.execute("INSERT INTO qr (id, type, district, organizer_name, timestamp, location) VALUES ('%s', '%s', %s, '%s', '%s', '%s');" % (form['qr_id'], form['type'], form['district'], form['organizer_name'], datetime.datetime.now().time().strftime("%H:%M:%S"), form['location']))
                con.commit()

                return "success"
            else:
                
                con.commit()
                return "district_full"
        except:
            con.rollback()

            raise
        finally:
            con.close()

    def organizer_history(self, organizer_name):
        con = Database.connect(self)
        cursor = con.cursor()

        cursor.execute("SELECT EXISTS(SELECT * FROM qr WHERE organizer_name='%s');" % organizer_name)
        check = cursor.fetchone()[0]
        
        if check == 0:
            return 0
        else:
            cursor.execute("select district from qr where organizer_name = '%s' order by timestamp desc limit 1;" % organizer_name)
            district = cursor.fetchone()[0]
            return district


    def map_district_data(self, district):
        con = Database.connect(self)
        cursor = con.cursor(pymysql.cursors.DictCursor)

        data = {}

        cursor.execute("SELECT fraction FROM districts WHERE log_type='occupation' AND id=%s" % district)
        data['occupied'] = cursor.fetchone()['fraction']
        
        if data['occupied'] != 0:
            return data
        
        cursor.execute("SELECT COUNT(*) AS pts FROM logs WHERE fraction=1 AND point_type='silver' AND district=%s" % district)
        data['points_rzem'] = cursor.fetchone()['pts']
        cursor.execute("SELECT COUNT(*) AS pts FROM logs WHERE fraction=2 AND point_type='silver' AND district=%s" % district)
        data['points_woj'] = cursor.fetchone()['pts']
        cursor.execute("SELECT COUNT(*) AS pts FROM logs WHERE fraction=3 AND point_type='silver' AND district=%s" % district)
        data['points_hand'] = cursor.fetchone()['pts']
        cursor.execute("SELECT COUNT(*) AS pts FROM logs WHERE fraction=4 AND point_type='silver' AND district=%s" % district)
        data['points_duch'] = cursor.fetchone()['pts']
        
        con.close()

        return data

    def cheat_check(self, patrol_id, cheat_id):
        try:
            con = Database.connect(self)
            cursor = con.cursor()

            cursor.execute("SELECT EXISTS(SELECT * FROM logs WHERE point_type='cheat' AND point_id=%s AND patrol_id=%s);" % (cheat_id, patrol_id))
            check = cursor.fetchone()[0]
            
            if check == 0:
                data = Database.patrol_data(self, patrol_id)
                cursor.execute("INSERT INTO logs (patrol_id, fraction, point_type, point_id, district, points, timestamp) VALUES (%s, %s, 'cheat', %s, 0, 0, '%s');" % (patrol_id, data['fraction'], cheat_id, datetime.datetime.now().time().strftime("%H:%M:%S")))
                con.commit()

                return True
            else:
                return False

        except:
            con.rollback()

            raise
        finally:
            con.close()


    def cheat_use(self, patrol_id, cheat_id):
        try:
            con = Database.connect(self)
            cursor = con.cursor()

            data = Database.patrol_data(self, patrol_id)
                
            cursor.execute("INSERT INTO logs (patrol_id, fraction, point_type, point_id, district, points, timestamp) VALUES (%s, %s, 'cheat_used', %s, 0, 0, '%s');" % (patrol_id, data['fraction'], cheat_id, datetime.datetime.now().time().strftime("%H:%M:%S")))
            con.commit()

            return True

        except:
            con.rollback()

            raise
        finally:
            con.close()


# **********************************************************************************
# FUNKCJE PANELU ADMINISTRATORA

    def admin_qr_data(self):
        con = Database.connect(self)
        cursor = con.cursor(pymysql.cursors.DictCursor)
        # cursor = con.cursor()

        data = []

        for i in range(1, 9):
            cursor.execute("SELECT * FROM qr WHERE district=%s ORDER BY district, type, timestamp ASC;" % i)
            district = cursor.fetchall()
            data.append(district)

        con.close()

        return data


    def admin_patrols_data(self):
        con = Database.connect(self)
        cursor = con.cursor(pymysql.cursors.DictCursor)

        active = {}
        cursor.execute("SELECT id, patrol_name, path, time, fraction, phone FROM patrols WHERE fraction IS NOT NULL ORDER BY path, patrol_name, time ASC;")
        active = cursor.fetchall()

        for i in range(len(active)):
            active[i]['phone'] = active[i]['phone'][:3] + "-" + active[i]['phone'][3:6] + "-" + active[i]['phone'][6:]

        inactive = {}
        cursor.execute("SELECT id, patrol_name, path, time, fraction, phone FROM patrols WHERE fraction IS NULL ORDER BY path, patrol_name;")
        inactive = cursor.fetchall()

        for i in range(len(inactive)):
            inactive[i]['phone'] = inactive[i]['phone'][:3] + "-" + inactive[i]['phone'][3:6] + "-" + inactive[i]['phone'][6:]

        con.close()

        return active, inactive


    def admin_generate_results(self):
        con = Database.connect(self)
        cursor = con.cursor(pymysql.cursors.DictCursor)
       
        try:
            cursor.execute("truncate table results")
            
            cursor.execute("select id from patrols where fraction is not null order by id")
            id = cursor.fetchall()

            for i in range(0, len(id)):
                patrol_id = id[i]['id']

                cursor.execute("select patrol_name as name from patrols where id=%s", patrol_id)
                patrol_name = cursor.fetchone()['name']

                cursor.execute("select path from patrols where id=%s", patrol_id)
                path = cursor.fetchone()['path']

                cursor.execute("select fraction from patrols where id=%s", patrol_id)
                fraction = cursor.fetchone()['fraction']

                cursor.execute("select COALESCE(sum(points),0) as sum from logs where patrol_id=%s", patrol_id)
                points = cursor.fetchone()['sum']

                cursor.execute("select IFNULL(time, 0) AS time from patrols where id=%s", patrol_id)
                time = cursor.fetchone()['time']

                cursor.execute("insert into results (patrol_id, patrol_name, path, fraction, points, time) values (%s, '%s', '%s', %s, %s, '%s')" % (patrol_id, patrol_name, path, fraction, points, time))
                con.commit()

            return True
        except:
            con.rollback()

            raise
        finally:
            con.close()


    def admin_generate_detailed_results(self):
        con = Database.connect(self)
        cursor = con.cursor(pymysql.cursors.DictCursor)
       
        try:
            cursor.execute("truncate table detailed_results")
            
            cursor.execute("select id from patrols where fraction is not null order by id")
            id = cursor.fetchall()

            for i in range(0, len(id)):
                patrol_id = id[i]['id']

                cursor.execute("select patrol_name as name from patrols where id=%s", patrol_id)
                patrol_name = cursor.fetchone()['name']

                cursor.execute("select path from patrols where id=%s", patrol_id)
                path = cursor.fetchone()['path']

                cursor.execute("select fraction from patrols where id=%s", patrol_id)
                fraction = cursor.fetchone()['fraction']

                cursor.execute("select COALESCE(sum(points),0) as sum from logs where patrol_id=%s", patrol_id)
                points = cursor.fetchone()['sum']

                cursor.execute("select IFNULL(time, 0) AS time from patrols where id=%s", patrol_id)
                time = cursor.fetchone()['time']

                cursor.execute("select COUNT(*) AS silver from logs where point_type='silver' and patrol_id=%s", patrol_id)
                silver = cursor.fetchone()['silver']

                cursor.execute("select COUNT(*) AS gold from logs where point_type='gold' and patrol_id=%s", patrol_id)
                gold = cursor.fetchone()['gold']

                cursor.execute("select COUNT(*) AS bonus from logs where point_type='bonus' and patrol_id=%s", patrol_id)
                bonus = cursor.fetchone()['bonus']

                cursor.execute("select exists(select * from logs where point_type='insignia' and point_id=1 and patrol_id=%s) as scepter", patrol_id)
                scepter = cursor.fetchone()['scepter']

                cursor.execute("select exists(select * from logs where point_type='insignia' and point_id=2 and patrol_id=%s) as apple", patrol_id)
                apple = cursor.fetchone()['apple']

                cursor.execute("select exists(select * from logs where point_type='insignia' and point_id=3 and patrol_id=%s) as sword", patrol_id)
                sword = cursor.fetchone()['sword']

                cursor.execute("select exists(select * from logs where point_type='coronation' and patrol_id=%s) as coronation", patrol_id)
                coronation = cursor.fetchone()['coronation']

                cursor.execute("select ifnull((select points from logs where point_type='character' and point_id=1 and patrol_id=%s), 0) as char_1;", patrol_id)
                char_1 = cursor.fetchone()['char_1']

                cursor.execute("select ifnull((select points from logs where point_type='character' and point_id=2 and patrol_id=%s), 0) as char_2;", patrol_id)
                char_2 = cursor.fetchone()['char_2']

                cursor.execute("select ifnull((select points from logs where point_type='character' and point_id=3 and patrol_id=%s), 0) as char_3;", patrol_id)
                char_3 = cursor.fetchone()['char_3']

                cursor.execute("select ifnull((select points from logs where point_type='character' and point_id=4 and patrol_id=%s), 0) as char_4;", patrol_id)
                char_4 = cursor.fetchone()['char_4']

                cursor.execute("select ifnull((select points from logs where point_type='character' and point_id=5 and patrol_id=%s), 0) as char_5;", patrol_id)
                char_5 = cursor.fetchone()['char_5']

                cursor.execute("select ifnull((select points from logs where point_type='character' and point_id=6 and patrol_id=%s), 0) as char_6;", patrol_id)
                char_6 = cursor.fetchone()['char_6']
                
                cursor.execute("select ifnull((select points from logs where point_type='character' and point_id=7 and patrol_id=%s), 0) as char_7;", patrol_id)
                char_7 = cursor.fetchone()['char_7']

                cursor.execute("select ifnull((select points from logs where point_type='character' and point_id=8 and patrol_id=%s), 0) as char_8;", patrol_id)
                char_8 = cursor.fetchone()['char_8']

                cursor.execute("insert into detailed_results (patrol_id, patrol_name, path, fraction, points, time, silver, gold, bonus, scepter, apple, sword, coronation, char_1, char_2, char_3, char_4, char_5, char_6, char_7, char_8) values (%s, '%s', '%s', %s, %s, '%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" % (patrol_id, patrol_name, path, fraction, points, time, silver, gold, bonus, scepter, apple, sword, coronation, char_1, char_2, char_3, char_4, char_5, char_6, char_7, char_8))
                con.commit()

            return True
        except:
            con.rollback()

            raise
        finally:
            con.close()


    def admin_get_results(self):
        con = Database.connect(self)
        cursor = con.cursor(pymysql.cursors.DictCursor)

        data = {}
        cursor.execute("SELECT * FROM results ORDER BY points DESC, time;")
        data = cursor.fetchall()

        con.close()

        return data


    def admin_reset_for_test(self):
        con = Database.connect(self)
        cursor = con.cursor()
       
        try: 
            cursor.execute("UPDATE districts SET fraction=0 WHERE log_type='occupation';")
            cursor.execute("TRUNCATE logs;")
            cursor.execute("UPDATE patrols SET fraction=NULL, time=NULL;")
            cursor.execute("DELETE FROM qr WHERE district NOT IN (1, 2);")
            con.commit()

            return True
        except:
            con.rollback()

            raise
        finally:
            con.close()


    def admin_insert_new_patrol(self, form):
        con = Database.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute("INSERT INTO patrols (patrol_name, path, people, phone) VALUES ('%s', '%s', %s, '%s');" % (form['patrol_name'], form['path'], form['people'], form['phone']))
            con.commit()

            return True
        except:
            con.rollback()

            raise
        finally:
            con.close()


    def admin_patrol_cheat(self, patrol_id, cheat_id):
        con = Database.connect(self)
        cursor = con.cursor()

        cursor.execute("SELECT EXISTS(SELECT * FROM logs WHERE point_type='cheat' AND point_id=%s AND patrol_id=%s);" % (cheat_id, patrol_id))
        check = cursor.fetchone()[0]

        if check == 0:
            return "unavailable"
        if check == 1:
            cursor.execute("SELECT EXISTS(SELECT * FROM logs WHERE point_type='cheat_used' AND point_id=%s AND patrol_id=%s);" % (cheat_id, patrol_id))
            state = cursor.fetchone()[0]
            
            if state == 0:
                return "available"
            if state == 1:
                return "used"


    def admin_logs(self):
        con = Database.connect(self)
        cursor = con.cursor()

        cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 30;")
        data = cursor.fetchall()

        con.close()
        return data
    

    def admin_insert_bonus(self, form):
        con = Database.connect(self)
        cursor = con.cursor()

        try:
            patrol_data = Database.patrol_data(self, form['patrol_id'])
            cursor.execute("INSERT INTO logs (patrol_id, fraction, point_type, point_id, points, timestamp) VALUES (%s, %s, 'bonus', %s, %s, '%s');" % (form['patrol_id'], patrol_data['fraction'], form['district'], 3, datetime.datetime.now().time().strftime("%H:%M:%S")))
            con.commit()

            return True
        except:
            con.rollback()

            raise
        finally:
            con.close()


    def admin_insert_insignum(self, form):
        con = Database.connect(self)
        cursor = con.cursor()

        try:
            patrol_data = Database.patrol_data(self, form['patrol_id'])
            cursor.execute("INSERT INTO logs (patrol_id, fraction, point_type, point_id, points, timestamp) VALUES (%s, %s, 'insignia', %s, %s, '%s');" % (form['patrol_id'], patrol_data['fraction'], form['insignium'], 0, datetime.datetime.now().time().strftime("%H:%M:%S")))
            con.commit()

            return True
        except:
            con.rollback()

            raise
        finally:
            con.close()


    def admin_update_points(self, form):
        con = Database.connect(self)
        cursor = con.cursor()

        try:
            cursor.execute("UPDATE logs SET points=%s WHERE patrol_id=%s AND point_type='character' AND point_id=%s;" % (form['points'], form['patrol_id'], form['district']))
            con.commit()

            return True
        except:
            con.rollback()

            raise
        finally:
            con.close()


# **********************************************************************************
# GENERATOR MAPY
    def generate_map(self):
        file_name = 'map_generator/script.sh'
        try:
            with open(file_name, "x", encoding="utf-8") as f:
                pass
        except FileExistsError:
            with open(file_name, "r+") as f:
                f.seek(0)
                f.truncate()

        with open(file_name, "a", encoding="utf-8") as f:
            map_file_name = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

            f.write("#!/bin/sh\n\n")

            f.write("cd map_generator\n")
            f.write("pwd\n")

            f.write("convert -size 1000x707 xc: \\\n")
            f.write("mapa.png -gravity center -composite \\\n")
            
            f.write("\\\n")

            for c in coordinates:
                data = Database.map_district_data(self, str(c[0])[1])
                
                if data['occupied'] != 0:
                    # rzem - woj - hand - duch
                    color = ["None", "#5d7163", "#884547", "#b89042", "#8ca6b1"]
                    cmd = "cd map_generator && convert " + c[0] + ".png -fill '" + color[data['occupied']] + "' -opaque '#bd9796' " + c[0] + "_col.png"
                    
                    os.system(cmd)
                    f.write(c[0] + "_col.png -gravity center -compose over -composite \\\n")
                else:
                    f.write(c[0] + ".png -gravity center -compose over -composite \\\n")
                    f.write(c[0] + "_arr.png -gravity center -composite \\\n")

                    f.write("-font MedievalSharp-Regular.ttf -fill black -pointsize 30 \\\n")

                    f.write("hand.png -gravity NorthWest -geometry +" + str(c[1]) + "+" + str(c[2]) + " -composite \\\n")
                    f.write("-gravity NorthWest -annotate +" + str(c[3]) + "+" + str(c[4]) + " '" + str(data['points_hand']) + "' \\\n")

                    f.write("duch.png -gravity NorthWest -geometry +" + str(c[5]) + "+" + str(c[6]) + " -composite \\\n")
                    f.write("-gravity NorthWest -annotate +" + str(c[7]) + "+" + str(c[8]) + " '" + str(data['points_duch']) + "' \\\n")

                    f.write("rzem.png -gravity NorthWest -geometry +" + str(c[9]) + "+" + str(c[10]) + " -composite \\\n")
                    f.write("-gravity NorthWest -annotate +" + str(c[11]) + "+" + str(c[12]) + " '" + str(data['points_rzem']) + "' \\\n")

                    f.write("woj.png -gravity NorthWest -geometry +" + str(c[13]) + "+" + str(c[14]) + " -composite \\\n")
                    f.write("-gravity NorthWest -annotate +" + str(c[15]) + "+" + str(c[16]) + " '" + str(data['points_woj']) + "' \\\n")

            f.write("\\\n")
            f.write("punkty.png -gravity center -composite \\\n")
            f.write("-layers flatten ../static/map/" + map_file_name + ".png")

        os.system("'map_generator/script.sh'")

        print("WYGENEROWANO NOWA MAPE: ", map_file_name)

        try:
            with open("map_generator/map_last_file_name", 'x') as f:
                f.write(map_file_name + ".png")
        except FileExistsError:
            with open("map_generator/map_last_file_name", "r+") as f:
                old_file = f.read()
                f.seek(0)
                f.write(map_file_name + ".png")
                f.truncate()

                list_files = os.listdir(var.map_dir_path)
                number_files = len(list_files)

                if number_files != 0:
                    list_files.sort()

                    if number_files > var.map_amount_limit:
                        for f in range(number_files-var.map_amount_limit):
                            print(list_files[f])
                            os.remove(var.map_dir_path + list_files[f])


                

        