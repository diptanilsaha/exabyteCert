from app import db, CERTIFICATE_FOLDER
from app.models import Participant
from app.main.forms import EmailForm
from app.main import bp
from flask import render_template, redirect, url_for, g, session, abort, send_from_directory

@bp.before_request
def set_participant():
    if 'participant' not in session.keys():
        session['participant'] = None
        return redirect(url_for('certs.index'))

    if session['participant'] != None:
        email = session['participant']
        participant = db.session.execute(db.select(Participant).filter_by(email=email)).first()
        g.participant = participant[0]


@bp.route("/", methods=['GET', 'POST'])
def index():
    if session['participant'] != None:
        return redirect(url_for('certs.certificates'))
    form = EmailForm()
    if form.validate_on_submit():
        session['participant'] = form.email.data
        return redirect(url_for('certs.certificates'))
    return render_template('index.html', form=form)


@bp.route("/certificates")
def certificates():
    if session['participant'] == None:
        return redirect(url_for('certs.index'))
    events = g.participant.events
    certs = {}
    for event in events:
        certs[event.event.name] = event.certificate
    return render_template('certificates.html', certs=certs)


@bp.route("/certificate/<path:filename>")
def certificate(filename):
    if session['participant'] == None:
        return redirect(url_for('certs.index'))

    certs = []
    for event in g.participant.events:
        certs.append(event.certificate)

    if filename not in certs:
        abort(403)
    return send_from_directory(CERTIFICATE_FOLDER, filename, as_attachment=True)


@bp.route("/logout")
def remove_participant():
    session['participant'] = None
    return redirect(url_for('certs.index'))
