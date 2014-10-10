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
    RedirectRoute('/', handlers.ManifestHandler, name='manifest', strict_slash=True),
    RedirectRoute('/secure/', handlers.SecureRequestHandler, name='secure', strict_slash=True),
    RedirectRoute('/gettest/', handlers.getTestFile, name='gettest', strict_slash=True),
    RedirectRoute('/test/', handlers.TestHandler, name='test', strict_slash=True),
    RedirectRoute('/add_vessel_data/', handlers.addVesselData, name='add_vessel_data', strict_slash=True),
    RedirectRoute('/save_manifest/', handlers.SaveManifestHandler, name='savemanifest', strict_slash=True),
    #first
    RedirectRoute('/save_manifest1/<keyval>', handlers.SaveManifestHandler1, name='savemanifest1', strict_slash=True),

    RedirectRoute('/serve/([^/]+)?', handlers.ServeHandler, name='serve_handler', strict_slash=True),

    RedirectRoute('/update_links/', handlers.UpdateLinks, name='updatelinks', strict_slash=True),

    RedirectRoute('/manifest/', handlers.ManifestHandler, name='manifest', strict_slash=True),
    RedirectRoute('/manifest_detail/<keyval>', handlers.ManifestDetailHandler, name='manifest_detail', strict_slash=True),
    #RedirectRoute('/vesselview/<keyval>', handlers.VesselHandler, name='vesselhandler', strict_slash=True),
    #RedirectRoute('/blobInfo/<keyval>', handlers.VesselHandler, name='vesselhandler', strict_slash=True),
    RedirectRoute('/results_handler/', handlers.ResultsHandler, name='results', strict_slash=True),
    RedirectRoute('/settings/delete_account', handlers.DeleteAccountHandler, name='delete-account', strict_slash=True),
    RedirectRoute('/contact/', handlers.ContactHandler, name='contact', strict_slash=True),
    RedirectRoute('/file_handler/([^/]+)?', handlers.ViewFileHandler, name='filehandler', strict_slash=True),
    RedirectRoute('/upload1', handlers.UploadHandler1, name='upload1', strict_slash=True),
    RedirectRoute('/filelist', handlers.FileListHandler, name='filelist', strict_slash=True),
    RedirectRoute('/containerlist/<filekey>/<sheet_name>', handlers.ContainerListHandler, name='containerlist', strict_slash=True),
    RedirectRoute('/sheetlist', handlers.FileListHandler, name='sheetlist', strict_slash=True),
    RedirectRoute('/readingslist/<filekey>/<sheet_name>/<row>', handlers.ReadingsListHandler, name='readingslist', strict_slash=True),
    RedirectRoute('/vessellist/<filekey>', handlers.VesselListHandler, name='vessellist', strict_slash=True),
]

def get_routes():
    return _routes

def add_routes(app):
    if app.debug:
        secure_scheme = 'http'
    for r in _routes:
        app.router.add(r)


