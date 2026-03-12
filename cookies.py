# Cookies in product version must be check for compatibility with domain name with and without "www"

from flask import Flask, request, make_response, redirect, url_for
import variables as var

def create_cookie(message, id, type):
    resp = redirect(url_for('message', text=message))

    resp.set_cookie('id', id, max_age=60*60*var.cookie_max_age)
    resp.set_cookie('type', type, max_age=60*60*var.cookie_max_age)

    return resp

def remove_cookies(message):
    resp = redirect(url_for('message', text=message))

    resp.delete_cookie('id')
    resp.delete_cookie('type')

    return resp

def create_cookie_admin(message):
    resp = redirect(url_for('message', text=message))

    resp.set_cookie('admin', 'oblicza', max_age=60*60*var.cookie_max_age)

    return resp