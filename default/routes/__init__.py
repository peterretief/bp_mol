"""
Using redirect route instead of simple routes since it supports strict_slash
Simple route: http://webapp-improved.appspot.com/guide/routing.html#simple-routes
RedirectRoute: http://webapp-improved.appspot.com/api/webapp2_extras/routes.html#webapp2_extras.routes.RedirectRoute
"""
from webapp2_extras.routes import RedirectRoute
from bp_content.themes.default.handlers import handlers

secure_scheme = 'https'

# Here go your routes, you can overwrite boilerplate routes (bp_includes/routes)

_routes = [
    RedirectRoute('/secure/', handlers.SecureRequestHandler, name='secure', strict_slash=True),
    RedirectRoute('/results_handler/', handlers.ResultsHandler, name='results', strict_slash=True),
    RedirectRoute('/settings/delete_account', handlers.DeleteAccountHandler, name='delete-account', strict_slash=True),
    RedirectRoute('/contact/', handlers.ContactHandler, name='contact', strict_slash=True),
    RedirectRoute('/file_handler/([^/]+)?', handlers.ViewFileHandler, name='filehandler', strict_slash=True),
    RedirectRoute('/upload', handlers.UploadHandler, name='upload', strict_slash=True),
    RedirectRoute('/filelist', handlers.FileListHandler, name='filelist', strict_slash=True),
    RedirectRoute('/containerlist/<container>/<sheet_name>', handlers.ContainerListHandler, name='containerlist', strict_slash=True),
    RedirectRoute('/sheetlist', handlers.FileListHandler, name='sheetlist', strict_slash=True),
    RedirectRoute('/templist/<temp>', handlers.FileListHandler, name='templist', strict_slash=True),
    RedirectRoute('/vessellist/<vessel>', handlers.VesselListHandler, name='vessellist', strict_slash=True),
]

def get_routes():
    return _routes

def add_routes(app):
    if app.debug:
        secure_scheme = 'http'
    for r in _routes:
        app.router.add(r)
