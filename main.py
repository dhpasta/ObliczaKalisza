from flask import Flask, flash, make_response, redirect, render_template, request, url_for, send_file
from database import Database
import variables as var
from cookies import *
from aws_sdk import EC2InstanceWrapper

import sys
import os
import pymysql
import traceback
import datetime

import qrcode
import base64
from io import BytesIO

app = Flask(__name__)
app.debug = True

db = Database()

db.generate_map()
print("Data: ", datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S"))

# Types of url params:
# ?type=patrol&id=99
# ?type=fraction&id=1
# ?type=qr&id=d8eg16gq
# ?type=insignia&id=1
# ?type=coronation
# ?type=time_stop

# Cookies types:
# patrol
# organizer
# character

@app.route('/')
def index():

    url_type = request.args.get('type', type = str)
    url_id = request.args.get('id', type = str)

    cookie_type = request.cookies.get('type')
    cookie_id = request.cookies.get('id')

    # Reveal results on home page

    # if datetime.datetime.now() >= var.home_page_results:
    #     if cookie_type == 'patrol':
    #         patrol_id = cookie_id
    #     else:
    #         patrol_id = ""

    #     data = db.admin_get_results()
    #     return render_template('main_page.html', results=data, patrol_id=patrol_id)

    try:
        # QR ON FRACTION (FELLOWSHIP) CARD
        if url_type == 'fraction':
            if cookie_type is None:
                easy_path, hard_path = db.register_patrol()
                return render_template('register_patrol.html', easy_path=easy_path, hard_path=hard_path, fraction=url_id)
            elif cookie_type == 'patrol':
                return redirect("/")

        # CHECKPOINT (QR CODE)
        if url_type == 'qr':
            if cookie_type == 'organizer':
                data = db.qr_data(id=url_id)
                organizer_history = db.organizer_history(organizer_name=cookie_id)
                if not data:
                    return render_template('register_qr.html', qr_id=url_id, organizer_name=cookie_id, organizer_history=organizer_history)
                else:
                    return redirect(url_for('message', text="Ten kod już jest zarejestrowany"))

            if cookie_type == 'patrol':
                check, qr_type = db.qr_patrol(qr_id=url_id, patrol_id=cookie_id)
                if not qr_type:
                    return redirect(url_for('message', text="Ten kod nie posiada żadnej funkcji! Zgłoś to organizatorom"))
                if qr_type == 'silver':
                    if check == "collected": return redirect(url_for('message', text="Ten kod już został zdobyty"))
                    if check == "find": return redirect(url_for('message', text="Zdobyłeś srebrny kod"))
                    if check == "takeover": return redirect(url_for('message', text="Twoja gildia zajmuje dzielnice"))
                    if check == "occupied": return redirect(url_for('message', text="Ta dzielnica jest już zdobyta"))
                if qr_type == 'gold':
                    if check:
                        hint = db.get_hint(patrol_id=cookie_id)
                        if hint:
                            return redirect(url_for('message', text="Zdobywasz podpowiedź! Zobaczysz ją na stronie patrolu!"))
                        else:
                            return redirect(url_for('message', text="Wszystkie wskazówki zdobyte"))
                    else:
                        return redirect(url_for('message', text="Już zdobyłeś ten złoty kod"))

        # PATROL QR CODE
        if url_type == 'patrol':
            if cookie_type == 'character':
                data = db.character_patrol_check(patrol_id=url_id, character_id=cookie_id)
                patrol_data = db.patrol_data(url_id)

                if data == 'already_visited':
                    return redirect(url_for('message', text="Ten patrol już odwiedził Wasz punkt"))
                else:
                    return render_template('character_form.html', patrol_id=url_id, character_id=cookie_id, district_owner=data, patrol_data=patrol_data)


        # BONUS QR CODE - INSIGNIA
        if url_type == 'insignia':
            if cookie_type == 'patrol':
                check = db.insignia(patrol_id=cookie_id, insignia_id=url_id)

                if check:
                    return redirect(url_for('message', text="Zdobyłeś insygnia"))
                else:
                    return redirect(url_for('message', text="Już posiadasz te insygnia"))

            else:
                return redirect('/')


        # BONUS QR CODE - KINGS CORONATION
        if url_type == 'coronation':
            if cookie_type == 'patrol':
                check = db.coronation(patrol_id=cookie_id)

                if check == 'success':
                    return redirect(url_for('message', text="Koronowałeś króla"))
                if check == 'unsatisfactorily':
                    return redirect(url_for('message', text="Nie spełniasz wymagań by koronować króla"))
                if check == 'already_corronated':
                    return redirect(url_for('message', text="Już otrzymałeś punkty za koronacje Króla"))

            else:
                return redirect('/')


        # BONUS QR CODE - CHEAT CARD
        if url_type == 'cheat':
            if cookie_type == 'patrol':
                patrol_data = db.patrol_data(cookie_id)
                if patrol_data['path'] == "hard":
                    check = db.cheat_check(patrol_id=cookie_id, cheat_id=url_id)

                    if check:
                        return redirect(url_for('message', text="Zdobyłeś kartę umiejętności"))
                    else:
                        return redirect(url_for('message', text="Już posiadasz tę kartę umiejętności!"))
                else:
                    return redirect(url_for('message', text="Karta umiejętności działa tylko w ścieżce zjednoczyciel"))

            else:
                return redirect('/')


        # CHECK OUT AT EVENT OFFICE
        if url_type == 'time_stop':                                        
            if cookie_type == 'patrol':
                db.time_stop(cookie_id)
                return redirect(url_for('message', text="Czas stop!"))
        
        
        # # # # # # # # #
        # PATROL HOME PAGE
        if cookie_type == 'patrol':
            data="www.oblicza-kalisza.pl/?type=patrol&id=" + cookie_id
            qr = qrcode.make(data)
            buffered = BytesIO()
            qr.save(buffered, format="PNG")
            qr_img_bytes = base64.b64encode(buffered.getvalue()).decode()

            patrol_data = db.patrol_data(cookie_id)
            map = map_get_file_name()

            return render_template('main_page.html', patrol=qr_img_bytes, patrol_data=patrol_data, map=map)


        # # # # # # # # #
        # CHARACTER HOME PAGE
        if cookie_type == 'character':
            if cookie_id in ("1", "2", "6", "7"):
                print("cookie id: ", cookie_id)
                data="www.oblicza-kalisza.pl/?type=cheat&id=1"
                qr = qrcode.make(data)
                buffered = BytesIO()
                qr.save(buffered, format="PNG")
                cheat_1 = base64.b64encode(buffered.getvalue()).decode()

                data="www.oblicza-kalisza.pl/?type=cheat&id=2"
                qr = qrcode.make(data)
                buffered = BytesIO()
                qr.save(buffered, format="PNG")
                cheat_2 = base64.b64encode(buffered.getvalue()).decode()

                data="www.oblicza-kalisza.pl/?type=cheat&id=3"
                qr = qrcode.make(data)
                buffered = BytesIO()
                qr.save(buffered, format="PNG")
                cheat_3 = base64.b64encode(buffered.getvalue()).decode()

                data="www.oblicza-kalisza.pl/?type=cheat&id=4"
                qr = qrcode.make(data)
                buffered = BytesIO()
                qr.save(buffered, format="PNG")
                cheat_4 = base64.b64encode(buffered.getvalue()).decode()

                data = db.character_data(cookie_id)

                return render_template('character_page.html', data=data, cheat_qr_1=cheat_1, cheat_qr_2=cheat_2, cheat_qr_3=cheat_3, cheat_qr_4=cheat_4)
            data = db.character_data(cookie_id)

            return render_template('character_page.html', data=data)


        # # # # # # # # #
        # ORGANIZER HOME PAGE
        if cookie_type == 'organizer':
            data = db.admin_qr_data()
            return render_template('organizer_page.html', data=data)


        # OTHER CASE - MAIN PAGE WITH GENERAL INFORMATION FOR OUTSIDERS
        if datetime.datetime.now() >= var.home_page_game:
            map = map_get_file_name()
            return render_template('main_page.html', map_homepage=map)
        else:
            return render_template('main_page.html')



    except (pymysql.Error, pymysql.Warning) as error:
        print("pymysql.Error: ", error, file=sys.stderr)
        return render_template('error.html')
    except TypeError:
        error = traceback.format_exc()
        print("TypeError: ", error, file=sys.stderr)
        return render_template('error.html')



# ********************************************************************************************
# PREVIOUS EDITION RESULTS DISPLAY (AVALIBLE FROM MAIN PAGE)
@app.route('/final_results_24') 
def final_results_24():
    data_easy, data_hard=db.get_final_results_24()

    return render_template('final_results_24.html', data_hard=data_hard, data_easy=data_easy)


# COMMON MESSAGES TEMPLATE 
@app.route('/message/<text>') 
def message(text):
    return render_template('message.html', text=text), {"Refresh": "5; url=/"}


# CREATE PATROL COOKIE
@app.route('/add_cookie_patrol', methods = ['POST']) 
def add_cookie_patrol(): 
    if request.method == 'POST' and request.form['save']:
        try:
            patrol_id = db.set_patrol_id(request.form)
            if patrol_id != None:
                resp = create_cookie(message="Telefon został przypisany do twojego patrolu", id=str(patrol_id), type='patrol')
            else:
                return redirect(url_for('message', text="Podałeś niepasujący numer telefonu! Zeskanuj kod ponownie i spróbuj jeszcze raz!"))

        except (pymysql.Error, pymysql.Warning) as error:
            print("pymysql.Error: ", error, file=sys.stderr)
            return render_template('error.html')
        except TypeError:
            error = traceback.format_exc()
            print("TypeError: ", error, file=sys.stderr)
            return render_template('error.html')
    else:
        return render_template('error.html', code='Błąd formularza html')
    
    return resp

# REMOVE COOKIE
@app.route('/remove_cookie')
def remove_cookie():
    resp = remove_cookies(message="Cofnięto uprawnienia gry miejskiej")

    return resp 

@app.route('/organizer') 
def organizer(): 
    return render_template('register_organizer.html')

# CREATE ORGANIZER COOKIE
@app.route('/register_organizer', methods = ['POST']) 
def register_organizer(): 
    if request.method == 'POST' and request.form['save']:
        try:
            resp = create_cookie(message="Przyznano uprawnienia organizatora gry miejskiej", id=request.form['name'], type='organizer')

        except (pymysql.Error, pymysql.Warning) as error:
            print("pymysql.Error: ", error, file=sys.stderr)
            return render_template('error.html')
        except TypeError:
            error = traceback.format_exc()
            print("TypeError: ", error, file=sys.stderr)
            return render_template('error.html')
    else:
        return render_template('error.html', code='Błąd formularza html')
    
    return resp

@app.route('/character') 
def character():
    data = db.characters_list()
    return render_template('register_character.html', data=data)

# CREATE CHARACTER COOKIE
@app.route('/register_character', methods = ['POST']) 
def register_character(): 
    if request.method == 'POST' and request.form['save']:
        try:
            resp = create_cookie(message="Przyznano uprawnienia punktowego gry miejskiej oblicza kalisza", id=request.form['id'], type='character')

        except (pymysql.Error, pymysql.Warning) as error:
            print("pymysql.Error: ", error, file=sys.stderr)
            return render_template('error.html')
        except TypeError:
            error = traceback.format_exc()
            print("TypeError: ", error, file=sys.stderr)
            return render_template('error.html')
    else:
        return render_template('error.html', code='Błąd formularza html')
    
    return resp

# MAINTAIN CHECKPOINT QR CODE
@app.route('/register_qr', methods = ['POST']) 
def register_qr(): 
    if request.method == 'POST' and request.form['save']:
        try:
            qr = db.register_qr(request.form)
            
            if qr == "success": return redirect(url_for('message', text="Poprawnie zarejestrowano kod"))
            if qr == "exists": return redirect(url_for('message', text="Ten kod jużjest zarejestrowany!"))
            if qr == "district_full": return redirect(url_for('message', text="Wybrana dzielnica ma już zgłoszoną maksymalną liczbę kodów"))

        except (pymysql.Error, pymysql.Warning) as error:
            print("pymysql.Error: ", error, file=sys.stderr)
            return render_template('error.html')
        except TypeError:
            error = traceback.format_exc()
            print("TypeError: ", error, file=sys.stderr)
            return render_template('error.html')
    else:
        return render_template('error.html', code='Błąd formularza html')


# GRANT POINTS FOR COMPLETED TASK
@app.route('/character_grant_points', methods = ['POST']) 
def character_grant_points(): 
    if request.method == 'POST' and request.form['save']:
        try:
            check = db.character_grant_points(request)
            if check:
                return redirect(url_for('message', text="Przyznano punkty patrolowi"))
            else:
                return redirect(url_for('message', text="Ten patrol już otrzymał punkty za wykonane zadania!"))

        except (pymysql.Error, pymysql.Warning) as error:
            print("pymysql.Error: ", error, file=sys.stderr)
            return render_template('error.html')
        except TypeError:
            error = traceback.format_exc()
            print("TypeError: ", error, file=sys.stderr)
            return render_template('error.html')
    else:
        return render_template('error.html', code='Błąd formularza html')


# PATROL SUMMARY AFTER RESULTS ANNOUNCEMENT
@app.route('/patrol_page_after/<id>')
def patrol_page_after(id):
    data="www.oblicza-kalisza.pl/?type=patrol&id=" + id
    qr = qrcode.make(data)
    buffered = BytesIO()
    qr.save(buffered, format="PNG")
    qr_img_bytes = base64.b64encode(buffered.getvalue()).decode()

    patrol_data = db.patrol_data(id)
    map = map_get_file_name()

    return render_template('main_page.html', patrol=qr_img_bytes, patrol_data=patrol_data, map=map)


# ********************************************************************************************
# ADMINISTRATION PANEL PAGES
# ADDITIONAL ADMIN COOKIE REQUIRED TO ACCESS EVERY PAGE
@app.route('/admin_permit')
def admin_permit():
    resp = create_cookie_admin(message="Przyznano dostęp do panelu administarota")
    return resp

@app.route('/admin') 
@app.route('/admin/<message>') 
def admin(message=""):
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        return render_template('admin/panel.html', message=message)

@app.route('/admin_qr') 
def admin_qr():
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        data = db.admin_qr_data()
        return render_template('admin/qr.html', data=data)

@app.route('/admin_patrols') 
def admin_patrols():
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        active, inactive = db.admin_patrols_data()
        return render_template('admin/patrols.html', active=active, inactive=inactive)

@app.route('/admin_results') 
def admin_results():
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        db.admin_generate_results()
        data = db.admin_get_results()
        return render_template('admin/results.html', data=data)

@app.route('/admin_functional_codes') 
def admin_functional_codes():
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        data="http://www.oblicza-kalisza.pl/remove_cookie"
        qr = qrcode.make(data)
        buffered = BytesIO()
        qr.save(buffered, format="PNG")
        img_remove_cookie = base64.b64encode(buffered.getvalue()).decode()

        data="http://www.oblicza-kalisza.pl/organizer"
        qr = qrcode.make(data)
        buffered = BytesIO()
        qr.save(buffered, format="PNG")
        img_organizer = base64.b64encode(buffered.getvalue()).decode()

        data="http://www.oblicza-kalisza.pl/character"
        qr = qrcode.make(data)
        buffered = BytesIO()
        qr.save(buffered, format="PNG")
        img_character = base64.b64encode(buffered.getvalue()).decode()

        data="http://www.oblicza-kalisza.pl/?type=time_stop"
        qr = qrcode.make(data)
        buffered = BytesIO()
        qr.save(buffered, format="PNG")
        img_time_stop = base64.b64encode(buffered.getvalue()).decode()


        return render_template('admin/functional_codes.html', img_remove_cookie=img_remove_cookie, img_organizer=img_organizer, img_character=img_character, img_time_stop=img_time_stop)


@app.route('/admin_functional_codes_testing') 
def admin_functional_codes_testing():
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        domain=EC2InstanceWrapper.display()
        print(domain)
        data="http://www.oblicza-kalisza.pl/remove_cookie"
        qr = qrcode.make(data)
        buffered = BytesIO()
        qr.save(buffered, format="PNG")
        img_remove_cookie = base64.b64encode(buffered.getvalue()).decode()

        data="http://www.oblicza-kalisza.pl/organizer"
        qr = qrcode.make(data)
        buffered = BytesIO()
        qr.save(buffered, format="PNG")
        img_organizer = base64.b64encode(buffered.getvalue()).decode()

        data="http://www.oblicza-kalisza.pl/character"
        qr = qrcode.make(data)
        buffered = BytesIO()
        qr.save(buffered, format="PNG")
        img_character = base64.b64encode(buffered.getvalue()).decode()

        data="http://www.oblicza-kalisza.pl/?type=time_stop"
        qr = qrcode.make(data)
        buffered = BytesIO()
        qr.save(buffered, format="PNG")
        img_time_stop = base64.b64encode(buffered.getvalue()).decode()


        return render_template('admin/functional_codes_testing.html', img_remove_cookie=img_remove_cookie, img_organizer=img_organizer, img_character=img_character, img_time_stop=img_time_stop)

@app.route('/admin_map') 
def admin_map():
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        map = map_get_file_name()

        return render_template('admin/map.html', map=map)

@app.route('/admin_generate_map') 
def admin_generate_map():
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        db.generate_map()
        map = map_get_file_name()

        return render_template('admin/map.html', map=map)

@app.route('/admin_reset_for_test') 
def admin_reset_for_test():
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        map = db.admin_reset_for_test()

        return redirect(url_for('admin', message="BAZA ZRESETOWANA"))

@app.route('/admin_patrol_page/<patrol_id>') 
def admin_patrol_page(patrol_id):
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        data = db.patrol_data(patrol_id)
        cheat_1 = db.admin_patrol_cheat(patrol_id, 1)
        cheat_2 = db.admin_patrol_cheat(patrol_id, 2)
        cheat_3 = db.admin_patrol_cheat(patrol_id, 3)
        cheat_4 = db.admin_patrol_cheat(patrol_id, 4)

        return render_template('admin/patrol_page.html', patrol_data=data, cheat_1=cheat_1, cheat_2=cheat_2, cheat_3=cheat_3, cheat_4=cheat_4)

@app.route('/admin_cheat_use/<patrol_id>/<cheat_id>') 
def admin_cheat_use(patrol_id, cheat_id):
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        db.cheat_use(patrol_id, cheat_id)
        return redirect(url_for('admin_patrol_page', patrol_id=patrol_id))

@app.route('/admin_characters') 
def admin_characters():
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        return render_template('admin/characters.html')

@app.route('/admin_character_page/<id>') 
def admin_character_page(id):
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        data = db.character_data(id)
        return render_template('admin/character_page.html', data=data)

@app.route('/admin_add_patrol') 
def admin_add_patrol():
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        return render_template('admin/add_patrol_form.html')

@app.route('/admin_insert_new_patrol', methods = ['POST']) 
def admin_insert_new_patrol():
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        if request.method == 'POST' and request.form['save']:
            try:
                db.admin_insert_new_patrol(request.form)
                return redirect(url_for('admin_patrols'))

            except (pymysql.Error, pymysql.Warning) as error:
                print("pymysql.Error: ", error, file=sys.stderr)
                return render_template('error.html')
            except TypeError:
                error = traceback.format_exc()
                print("TypeError: ", error, file=sys.stderr)
                return render_template('error.html')
        else:
            return render_template('error.html', code='Błąd formularza html')

@app.route('/admin_logs/') 
def admin_logs():
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        data = db.admin_logs()
        return render_template('admin/logs.html', data=data)

@app.route('/admin_add_bonus') 
def admin_add_bonus():
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        return render_template('admin/add_bonus.html')

@app.route('/admin_insert_bonus', methods = ['POST']) 
def admin_insert_bonus():
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        if request.method == 'POST' and request.form['save']:
            try:
                db.admin_insert_bonus(request.form)
                return redirect(url_for('admin_patrol_page', patrol_id=request.form['patrol_id']))

            except (pymysql.Error, pymysql.Warning) as error:
                print("pymysql.Error: ", error, file=sys.stderr)
                return render_template('error.html')
            except TypeError:
                error = traceback.format_exc()
                print("TypeError: ", error, file=sys.stderr)
                return render_template('error.html')
        else:
            return render_template('error.html', code='Błąd formularza html')
        

@app.route('/admin_add_insignum') 
def admin_add_insignum():
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        return render_template('admin/add_insignum.html')

@app.route('/admin_insert_insignum', methods = ['POST']) 
def admin_insert_insignum():
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        if request.method == 'POST' and request.form['save']:
            try:
                db.admin_insert_insignum(request.form)
                return redirect(url_for('admin_patrol_page', patrol_id=request.form['patrol_id']))

            except (pymysql.Error, pymysql.Warning) as error:
                print("pymysql.Error: ", error, file=sys.stderr)
                return render_template('error.html')
            except TypeError:
                error = traceback.format_exc()
                print("TypeError: ", error, file=sys.stderr)
                return render_template('error.html')
        else:
            return render_template('error.html', code='Błąd formularza html')
        

@app.route('/admin_change_points') 
def admin_change_points():
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        return render_template('admin/change_points.html')

@app.route('/admin_update_points', methods = ['POST']) 
def admin_update_points():
    if not request.cookies.get('admin'):
        return redirect(url_for('message', text="BRAK DOSTĘPU"))
    else:
        if request.method == 'POST' and request.form['save']:
            try:
                db.admin_update_points(request.form)
                return redirect(url_for('admin_patrol_page', patrol_id=request.form['patrol_id']))

            except (pymysql.Error, pymysql.Warning) as error:
                print("pymysql.Error: ", error, file=sys.stderr)
                return render_template('error.html')
            except TypeError:
                error = traceback.format_exc()
                print("TypeError: ", error, file=sys.stderr)
                return render_template('error.html')
        else:
            return render_template('error.html', code='Błąd formularza html')


@app.route('/admin_detailed_results') 
def admin_detailed_results():
    db.admin_generate_detailed_results()
    return redirect(url_for('message', text="WYGENEROWANO"))

# ********************************************************************************************
# GET NEWEST MAP FILENAME
def map_get_file_name():
    with open("map_generator/map_last_file_name", "r") as f:
        map_last_file_name = "map/" + f.read()

        return map_last_file_name