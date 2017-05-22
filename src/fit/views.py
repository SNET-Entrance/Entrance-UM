import base64
import json
import csv
import uuid
import os
import itertools
import time
from subprocess import call

from flask import request, make_response
from flask_user import login_required, current_user

from bootstrap import db
from const import basedir
from fit import fit, models


@fit.route('/', methods=['GET'])
@login_required
def get_fitfiles():
    fitfiles = models.FitFile.query.filter_by(user_id=current_user.id)
    return make_response(json.dumps([f.dict() for f in fitfiles], default=date_handler), 200)

@fit.route('/<file_id>', methods=['GET'])
@login_required
def get_fitfile(file_id):
    fitfile = models.FitFile.query.filter_by(id=file_id).first_or_404()
    if fitfile not in current_user.fitfiles:
        return make_response('', 403)

    out = fitfile.dict()
    try:
        f = open(os.path.join(basedir, 'fitness', fitfile.path), 'r')
        csvfile = csv.reader(f)
        fieldnames = csvfile.next()
        fieldnames = [field.replace('.', '_').replace('[', '_').replace(']', '').replace('/', '_') for field in
                      fieldnames]

        reader = csv.DictReader(f, fieldnames=fieldnames)
        i = 0
        records = []
        for row in reader:
            i += 1
            if i == 1:
                continue
            records.append(json.dumps(row))

        out['records'] = records
    except IOError:
        return make_response('', 500)

    return make_response(json.dumps(out, default=date_handler), 200)


@fit.route('/', methods=['POST'])
@login_required
# processes an incoming *.fit file using FitCSVTool.jar. As result two *.csv files are stored in the filesystem.
def add_fitfile():
    if not os.path.exists(os.path.join(basedir, 'fitness')):
        os.makedirs(os.path.join(basedir, 'fitness'))
    if not os.path.exists(os.path.join(basedir, 'fitness', 'tmp')):
        os.makedirs(os.path.join(basedir, 'fitness', 'tmp'))
    if not os.path.exists(os.path.join(basedir, 'fitness', str(current_user.id))):
        os.makedirs(os.path.join(basedir, 'fitness', str(current_user.id)))

    file = request.files['file']
    filename = str(uuid.uuid1())
    tmp_path = os.path.join(basedir, 'fitness', 'tmp', filename)
    jar_path = os.path.join(os.getcwd(), 'fit', 'FitCSVTool.jar')
    target_path = os.path.join(basedir, 'fitness', str(current_user.id), filename)

    try:
        content = file.read()
        file = open(tmp_path, 'w')
        file.write(content)
        file.flush()
        os.fsync(file)
        file.close()
        cmd = 'java -jar ' + jar_path + ' -b ' + tmp_path + ' ' + target_path + '.csv'
        call(cmd, shell=True)
    except Exception:
        return make_response('IOError', 500)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    activity_datetime = extract_ActivityDateTime(target_path + '.csv')
    fitfile = models.FitFile('record_' + time.strftime("%d-%m-%Y-%H-%M-%S"), target_path + '_data.csv', current_user.id, activity_datetime)
    db.session.add(fitfile)
    db.session.commit()

    return make_response(json.dumps(fitfile.dict(), default=date_handler), 200)


@fit.route('/fitfile', methods=['POST'])
@login_required
def add_fitfile_admin():
    if not os.path.exists(os.path.join(basedir, 'fitness')):
        os.makedirs(os.path.join(basedir, 'fitness'))
    if not os.path.exists(os.path.join(basedir, 'fitness', 'tmp')):
        os.makedirs(os.path.join(basedir, 'fitness', 'tmp'))
    if not os.path.exists(os.path.join(basedir, 'fitness', str(current_user.id))):
        os.makedirs(os.path.join(basedir, 'fitness', str(current_user.id)))

    filename = str(uuid.uuid1())
    target_path = os.path.join(basedir, 'fitness', str(current_user.id), filename) + '_data.csv'

    data = base64.b64decode(request.data)
    filename = str(uuid.uuid1())
    try:
        f = open(target_path, 'w')
        f.write(data)
        f.close()
    except IOError:
        return make_response('', 500)

    fitfile = models.FitFile('record_' + time.strftime("%d-%m-%Y-%H-%M-%S"), target_path, current_user.id)
    db.session.add(fitfile)
    db.session.commit()

    return make_response(json.dumps(fitfile.dict(), default=date_handler), 200)


@fit.route('/<file_id>', methods=['DELETE'])
@login_required
def delete_fitfile(file_id):
    fitfile = models.FitFile.query.filter_by(id=file_id).first_or_404()

    if fitfile not in current_user.fitfiles:
        return make_response('', 403)

    # both csv files will be deleted from filesystem and db.
    path = os.path.join(basedir, 'fitness', fitfile.path + '_data.csv')
    if os.path.exists(path):
        os.remove(path)

    path2 = os.path.join(basedir, 'fitness', fitfile.path + '.csv')
    if os.path.exists(path2):
        os.remove(path2)

    db.session.delete(fitfile)
    db.session.commit()

    return make_response('', 200)


def date_handler(obj): return obj.isoformat() if hasattr(obj, 'isoformat') else obj

def extract_ActivityDateTime(path):
    # open file in read+binary mode
    with open(path, 'rb') as file:
        #dialect = csv.Sniffer().sniff(file.read(1024))
        text_temp = next(itertools.islice(csv.reader(file), 2, 7))
        t2 = int(text_temp[7])
        t3 = 631065600 # dmttime since 1989 12 31 00:00:00
        t4 = t3 + t2 # calculate true activity date and time
        t5 =  time.strftime("%d-%m-%Y at %H-%M-%S", time.gmtime(t4)) # convert true activity date and time
    return t5

