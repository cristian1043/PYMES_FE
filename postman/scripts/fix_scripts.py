import os

base = os.path.join(os.path.dirname(__file__), '..', 'collections', 'auth (listo)')

# ---- login ----
login_content = (
    '$kind: http-request\r\n'
    'name: login\r\n'
    "url: '{{base_url}}/auth/login'\r\n"
    'method: POST\r\n'
    'headers:\r\n'
    '  - key: Content-Type\r\n'
    '    value: application/json\r\n'
    'body:\r\n'
    '  type: json\r\n'
    '  content: |-\r\n'
    '    {\r\n'
    '        "username": "admin@pymesoft.com",\r\n'
    '        "password_hash": "123456"\r\n'
    '    }\r\n'
    'scripts:\r\n'
    '  - type: afterResponse\r\n'
    '    language: text/javascript\r\n'
    '    code: |-\r\n'
    '      pm.test("Status 200 OK", function () {\r\n'
    '          pm.response.to.have.status(200);\r\n'
    '      });\r\n'
    '\r\n'
    '      pm.test("Response has exito=true", function () {\r\n'
    '          const json = pm.response.json();\r\n'
    '          pm.expect(json.exito).to.be.true;\r\n'
    '      });\r\n'
    '\r\n'
    '      pm.test("Response contains access_token", function () {\r\n'
    '          const json = pm.response.json();\r\n'
    '          pm.expect(json).to.have.property("access_token");\r\n'
    '          pm.expect(json.access_token).to.be.a("string").and.not.empty;\r\n'
    '      });\r\n'
    '\r\n'
    '      pm.test("Response contains refresh_token", function () {\r\n'
    '          const json = pm.response.json();\r\n'
    '          pm.expect(json).to.have.property("refresh_token");\r\n'
    '      });\r\n'
    '\r\n'
    '      pm.test("Response contains usuario object", function () {\r\n'
    '          const json = pm.response.json();\r\n'
    '          pm.expect(json).to.have.property("usuario");\r\n'
    '          pm.expect(json.usuario).to.be.an("object");\r\n'
    '      });\r\n'
    '\r\n'
    '      // Save token to environment for subsequent requests\r\n'
    '      const json = pm.response.json();\r\n'
    '      if (json.access_token) {\r\n'
    '          pm.environment.set("token", json.access_token);\r\n'
    '      }\r\n'
    'order: 1000000000001000\r\n'
)

login_path = os.path.join(base, 'login.request.yaml')
with open(login_path, 'wb') as f:
    f.write(login_content.encode('utf-8'))
print('login done')

# ---- registro ----
registro_content = (
    '$kind: http-request\r\n'
    'name: registro\r\n'
    "url: '{{base_url}}/auth/register'\r\n"
    'method: POST\r\n'
    'headers:\r\n'
    '  - key: Content-Type\r\n'
    '    value: application/json\r\n'
    'body:\r\n'
    '  type: json\r\n'
    '  content: |-\r\n'
    '    {\r\n'
    '        "tipo_documento": "CC",\r\n'
    '        "documento": "1001234567",\r\n'
    '        "nombre": "Admin",\r\n'
    '        "apellido": "Sistema",\r\n'
    '        "email": "admin@pymesoft.com",\r\n'
    '        "telefono": "3001234567",\r\n'
    '        "username": "admin",\r\n'
    '        "password_hash": "123456",\r\n'
    '        "id_rol": 1\r\n'
    '    }\r\n'
    'scripts:\r\n'
    '  - type: afterResponse\r\n'
    '    language: text/javascript\r\n'
    '    code: |-\r\n'
    '      pm.test("Status 201 Created or 200 OK", function () {\r\n'
    '          pm.expect(pm.response.code).to.be.oneOf([200, 201]);\r\n'
    '      });\r\n'
    '\r\n'
    '      pm.test("Response is JSON", function () {\r\n'
    '          pm.response.to.be.json;\r\n'
    '      });\r\n'
    '\r\n'
    '      pm.test("Response contains usuario or id field", function () {\r\n'
    '          const json = pm.response.json();\r\n'
    '          pm.expect(json).to.satisfy(function(j) {\r\n'
    '              return j.hasOwnProperty("usuario") || j.hasOwnProperty("id") || j.hasOwnProperty("exito");\r\n'
    '          });\r\n'
    '      });\r\n'
    'order: 1000000000002000\r\n'
)

registro_path = os.path.join(base, 'registro.request.yaml')
with open(registro_path, 'wb') as f:
    f.write(registro_content.encode('utf-8'))
print('registro done')

# ---- perfil ----
perfil_content = (
    '$kind: http-request\r\n'
    'name: perfil (me)\r\n'
    "url: '{{base_url}}/auth/me'\r\n"
    'method: GET\r\n'
    'headers:\r\n'
    '  - key: Authorization\r\n'
    "    value: 'Bearer {{token}}'\r\n"
    'scripts:\r\n'
    '  - type: afterResponse\r\n'
    '    language: text/javascript\r\n'
    '    code: |-\r\n'
    '      pm.test("Status 200 OK", function () {\r\n'
    '          pm.response.to.have.status(200);\r\n'
    '      });\r\n'
    '\r\n'
    '      pm.test("Response is JSON", function () {\r\n'
    '          pm.response.to.be.json;\r\n'
    '      });\r\n'
    '\r\n'
    '      pm.test("Response contains user identity fields", function () {\r\n'
    '          const json = pm.response.json();\r\n'
    '          pm.expect(json).to.satisfy(function(j) {\r\n'
    '              return j.hasOwnProperty("email") || j.hasOwnProperty("username") || j.hasOwnProperty("id");\r\n'
    '          });\r\n'
    '      });\r\n'
    '\r\n'
    '      pm.test("Response time is under 2000ms", function () {\r\n'
    '          pm.expect(pm.response.responseTime).to.be.below(2000);\r\n'
    '      });\r\n'
    'order: 1000000000003000\r\n'
)

perfil_path = os.path.join(base, 'perfil.request.yaml')
with open(perfil_path, 'wb') as f:
    f.write(perfil_content.encode('utf-8'))
print('perfil done')
