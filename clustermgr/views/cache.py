"""A Flask blueprint with the views and logic dealing with the Cache Management
of Gluu Servers"""
import os

from flask import Blueprint, render_template, url_for, flash, redirect, \
    jsonify, request, session

from flask_login import login_required

from clustermgr.models import Server, AppConfiguration
from clustermgr.tasks.cache import install_cache_cluster


from ..core.license import license_reminder
from ..core.license import prompt_license
from ..core.license import license_required
from clustermgr.core.remote import RemoteClient
from clustermgr.core.utils import get_redis_config, get_cache_servers
from clustermgr.forms import CacheSettingsForm

cache_mgr = Blueprint('cache_mgr', __name__, template_folder='templates')
cache_mgr.before_request(prompt_license)
cache_mgr.before_request(license_required)
cache_mgr.before_request(license_reminder)


@cache_mgr.route('/')
@login_required
def index():
    servers = Server.query.all()
    appconf = AppConfiguration.query.first()
    

    
    if not appconf:
        flash("The application needs to be configured first. Kindly set the "
              "values before attempting clustering.", "warning")
        return redirect(url_for("index.app_configuration"))

    if not servers:
        flash("Add servers to the cluster before attempting to manage cache",
              "warning")
        return redirect(url_for('index.home'))


    if appconf.external_load_balancer:
        c_host = appconf.cache_host
        c_ip = appconf.cache_ip
    else:
        c_host = appconf.nginx_host
        c_ip = appconf.nginx_ip
        


    c = RemoteClient(host=c_host, ip=c_ip)
    
    try:
        c.startup()
    except:
        flash("SSH connection can't be established to cache server", "warning")

    result = c.get_file('/etc/stunnel/stunnel.conf')
    
    installed_servers = []

    if result[0]:
        installed_servers = get_redis_config(result[1])
    

    version = int(appconf.gluu_version.replace(".", ""))
    if version < 311:
        flash("Cache Management is available only for clusters configured with"
              " Gluu Server version 3.1.1 and above", "danger")
        return redirect(url_for('index.home'))

    form = CacheSettingsForm()

    cache_servers = get_cache_servers()

    return render_template('cache_index.html', 
                           servers=servers, 
                           form=form,
                           cache_servers=cache_servers,
                           )


def get_servers_and_list():
    server_id = request.args.get('id')
    
    if server_id:
        servers = [ Server.query.get(int(server_id)) ]
    else:
        servers = Server.query.all()

    server_id_list = [ s.id for s in servers ]
    
    return servers, server_id_list, server_id

@cache_mgr.route('/install/', methods=['GET', 'POST'])
@login_required
def install():

    cache_servers = get_cache_servers()
    servers = Server.query.all()

    if not servers:
        return redirect(url_for('cache_mgr.index'))


    task = install_cache_cluster.delay()
    
    
    
    return render_template( 'cache_install_logger.html',
                            servers=cache_servers+servers,
                            step=1,
                            task_id=task.id,
                           )


@cache_mgr.route('/status/')
@login_required
def get_status():

    status={'redis':{}, 'stunnel':{}}
    servers = Server.query.all()
    
    check_cmd = 'python -c "import socket;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);print s.connect_ex((\'{0}\', {1}))"'
    
    cache_servers = get_cache_servers()
    
    for server in servers + cache_servers:
        key = server.ip.replace('.','_')

        c = RemoteClient(host=server.hostname, ip=server.ip)
        try:
            c.startup()
        except:
            status['stunnel'][key] = False
            status['redis'][key] = False
        else:

            if server in cache_servers:
                r = c.run(check_cmd.format('localhost', 6379))
                stat = r[1].strip()
                
                if stat == '0':
                    status['redis'][key]=True
                else:
                    status['redis'][key]=False

                r = c.run(check_cmd.format(server.ip, 8000))
                stat = r[1].strip()

                if stat == '0':
                    status['stunnel'][key]=True
                else:
                    status['stunnel'][key]=False

            else:
                r = c.run(check_cmd.format('localhost', 8000))
                stat = r[1].strip()

                if stat == '0':
                    status['stunnel'][key]=True
                else:
                    status['stunnel'][key]=False

        c.close()
    
    return jsonify(status)

