import os
import csv
import yaml
import click
import secrets
from app import db, CERTIFICATE_FOLDER
from app.main import bp
from app.utils.cert import Certificate
from app.models import Participant, Event, Participation


@bp.cli.command("create-events", short_help="Create multiple new events.")
@click.option("-e", "--event", "eventnames", multiple=True, type=str, help="New Event Names.")
def create_events(eventnames):
    """Create multiple new events."""
    events = db.session.execute(db.select(Event)).all()
    events_list = []
    for event in events:
        events_list.append(event[0].name)

    for event in eventnames:
        if event not in events_list:
            try:
                e = Event(name=event)
                db.session.add(e)
                db.session.commit()
            except Exception:
                click.echo("Event %r could not be created." % event)
            else:
                click.echo("Event %r created." % event)
        else:
            click.echo("Event %r already present." % event)


@bp.cli.command("show-events", short_help="Show existing events.")
def show_events():
    """Display existing events."""
    events = db.session.execute(db.Select(Event).order_by(Event.name))
    events = events.all()

    if len(events) == 0:
        click.echo("No Events.")
    else:
        click.echo("Events:")
        for event in events:
            click.echo(event[0].name)


@bp.cli.command("delete-event", short_help="Delete an existing event.")
@click.option("-e", "--event", "eventname", type=str, help="Name of an existing event.")
def delete_event(eventname):
    """Delete an existing event."""
    event = db.session.execute(db.Select(Event).filter_by(name=eventname)).first()

    if event != None:
        event = event[0]
        participations = event.participants
        p_count = len(participations)
        certs = []
        for participation in participations:
            certs.append(participation.certificate)
        flag = True
        if p_count != 0:
            click.echo(f"WARNING! There are {p_count} participants under '{eventname}'!")
            flag = click.confirm('Do you want to continue?')
        if flag:
            try:
                db.session.delete(event)
                db.session.commit()
                for cert in certs:
                    os.remove(os.path.join(CERTIFICATE_FOLDER, cert))
            except:
                click.echo("Event %r could not be deleted." % event[0].name)
            else:
                click.echo("Event %r deleted." % event.name)
        else:
            click.echo("Deletion of Event %r cancelled." % eventname)
    else:
        click.echo("Event %r not found." % eventname)


@bp.cli.command("update-event", short_help="Update name of an existing event.")
@click.option("-o", "--old", "oldevent", type=str, help="Name of an existing event.")
@click.option("-n", "--new", "newevent", type=str, help="New name for the existing event.")
def update_event(oldevent, newevent):
    """Update name of an existing event."""
    event = db.session.execute(db.select(Event).filter_by(name=oldevent)).first()

    if event:
        event = event[0]
        try:
            event.name = newevent
            db.session.commit()
        except:
            click.echo('Event %r could not be updated.' % oldevent)
        else:
            click.echo('Event %r updated to %r.' % (oldevent, event.name))
    else:
        click.echo('Event %r not found.' % oldevent)


@bp.cli.command("generate-certs", short_help="Generate Certificates.")
@click.option('-y', '--yml', 'yamlfile', type=click.Path(exists=True), help="YAML file containing configuration.")
@click.option('-c', '--csv', 'eventfile', type=click.Path(exists=True), help="CSV file containing participant name.")
@click.option('-e', '--event', 'eventname', type=str, help="Event name")
def generate_certificates(yamlfile, eventfile, eventname):
    """
    Generates Certifcates from a CSV File for the given event and Certificates Configuration.

    YAML File must follow the following format:

    \b
    config.yml
    ----------
    template: <PATH>
    font:
        name: <PATH>
        size: <INT>
    participantBox: <LIST>
    eventBox: <LIST>
    title: <STR>
    author: <STR>


    CSV File must follow the following format:

    \b
    participation.csv
    -----------------
    name,email
    <NAME>,<EMAIL>

    Event must be created first before running this command.
    """

    directory = CERTIFICATE_FOLDER
    # certs/: Directory of Certificate.

    p_data = []
    # Participant data
    event_name = eventname

    with open(yamlfile, 'r') as file:
        config = yaml.safe_load(file)

    c_flag = Certificate.check_config(config)
    # Checking format of yamlfile and existence of template file and font file.
    if c_flag:
        if c_flag == 1:
            click.echo(f"Format of {yamlfile} is not correct.")
        elif c_flag == 2:
            click.echo(f"Format of Font name and Size are not correct.")
        elif c_flag == 3:
            click.echo(f"Template file doesn't exists. Check YAML File.")
        elif c_flag == 5:
            click.echo(f"Font File file doesn't exists. Check YAML File.")
        return

    certificate = Certificate(config)
    # Initializing Certificate Object.

    # Appending Participant data from csvfile.
    with open(eventfile, newline='') as csvFile:
        reader = csv.DictReader(csvFile)
        for row in reader:
            p_data.append(row)

    # Checking the format of CSV file.
    csv_keys = ['name', 'email']
    for key in csv_keys:
        if key not in p_data[0].keys():
            click.echo(f"Format of {eventfile} is not correct.")
            return

    # Finding event in db.
    event = db.session.execute(db.Select(Event).filter_by(name=event_name)).first()

    # Checking if event exists or not. If event does not exist, exit.
    if event == None:
        click.echo(f"{event_name} not found.")
        return
    else:
        event = event[0]

    for participation in p_data:
        p = db.session.execute(db.select(Participant).filter_by(email=participation['email'])).first()

        if p == None:
            try:
                p = Participant()
                p.name = participation['name']
                p.email = participation['email']
                db.session.add(p)
                db.session.commit()
            except:
                click.echo(f"{participation['name']} could not be created. Skipped.")
                continue
        else:
            p = p[0]
            participant_events = p.events
            # Loading Participant on p as participant already exists.
            flag = False
            for e in participant_events:
                # checking participation exists or not
                # if Participation exists then skips this participant.
                if e.event.name == event_name:
                    flag = True
                    click.echo(f"{event_name}: {participation['name']}, already created. {e.certificate}")
                    # Prints the old certificate details.
                    break
            if flag:
                # As participation already exists therefore, it continues.
                continue

        c_no = secrets.token_hex(28)
        # Creating certificate file name
        filename = os.path.join(directory, c_no)
        # Joining the certificate file name with directory
        certificate.create(participation['name'], event_name, filename)
        # Creating Certificate.
        try:
            part = Participation(
                participant = p,
                event = event,
                certificate = f"{c_no}.pdf"
            )
            db.session.add(part)
            db.session.commit()
        except Exception as e:
            os.remove(f"{filename}.pdf")
            click.echo(f"{event_name}: {participation['name']}, certificate could not be created. Skipped.")
        else:
            click.echo(f"{event_name}: {participation['name']} certificate created. ({c_no}.pdf)")
