import os

base = os.path.join(os.path.dirname(__file__), '..', 'collections', 'auth (listo)')

# ---- login ----
login_scripts = (
    'scripts:\n'
    '  - type: afterResponse\n'
    '    language: text/javascript\n'
    '    code: |-\n'
    '      pm.test("Status 200 OK", function () {\n'
    '          pm.response.to.have.status(200);\n'
    '      });\n'
    '\n'
    '      pm.test("Response has exito=true", function () {\n'
    '          const json = pm.response.json();\n'
    '          pm.expect(json.exito).to.be.true;\n'
    '      });\n'
    '\n'
    '      pm.test("Response contains access_token", function () {\n'
    '          const json = pm.response.json();\n'
    '          pm.expect(json).to.have.property("access_token");\n'
    '          pm.expect(json.access_token).to.be.a("string").and.not.empty;\n'
    '      });\n'
    '\n'
    '      pm.test("Response contains refresh_token", function () {\n'
    '          const json = pm.response.json();\n'
    '          pm.expect(json).to.have.property("refresh_token");\n'
    '      });\n'
    '\n'
    '      pm.test("Response contains usuario object", function () {\n'
    '          const json = pm.response.json();\n'
    '          pm.expect(json).to.have.property("usuario");\n'
    '          pm.expect(json.usuario).to.be.an("object");\n'
    '      });\n'
    '\n'
    '      // Save token to environment for subsequent requests\n'
    '      const json = pm.response.json();\n'
    '      if (json.access_token) {\n'
    '          pm.environment.set("token", json.access_token);\n'
    '      }\n'
    'order: 1000000000001000\n'
)

login_path = os.path.join(base, 'login.request.yaml')
with open(login_path, 'rb') as f:
    content = f.read().decode('utf-8')
new_content = content.replace('order: 1000000000001000\r\n', login_scripts).replace('order: 1000000000001000\n', login_scripts)
with open(login_path, 'wb') as f:
    f.write(new_content.encode('utf-8'))
print('login done')

# ---- registro ----
registro_scripts = (
    'scripts:\n'
    '  - type: afterResponse\n'
    '    language: text/javascript\n'
    '    code: |-\n'
    '      pm.test("Status 201 Created or 200 OK", function () {\n'
    '          pm.expect(pm.response.code).to.be.oneOf([200, 201]);\n'
    '      });\n'
    '\n'
    '      pm.test("Response is JSON", function () {\n'
    '          pm.response.to.be.json;\n'
    '      });\n'
    '\n'
    '      pm.test("Response contains usuario or id field", function () {\n'
    '          const json = pm.response.json();\n'
    '          pm.expect(json).to.satisfy(function(j) {\n'
    '              return j.hasOwnProperty("usuario") || j.hasOwnProperty("id") || j.hasOwnProperty("exito");\n'
    '          });\n'
    '      });\n'
    'order: 1000000000002000\n'
)

registro_path = os.path.join(base, 'registro.request.yaml')
with open(registro_path, 'rb') as f:
    content = f.read().decode('utf-8')
new_content = content.replace('order: 1000000000002000\r\n', registro_scripts).replace('order: 1000000000002000\n', registro_scripts)
with open(registro_path, 'wb') as f:
    f.write(new_content.encode('utf-8'))
print('registro done')

# ---- perfil ----
perfil_scripts = (
    'scripts:\n'
    '  - type: afterResponse\n'
    '    language: text/javascript\n'
    '    code: |-\n'
    '      pm.test("Status 200 OK", function () {\n'
    '          pm.response.to.have.status(200);\n'
    '      });\n'
    '\n'
    '      pm.test("Response is JSON", function () {\n'
    '          pm.response.to.be.json;\n'
    '      });\n'
    '\n'
    '      pm.test("Response contains user identity fields", function () {\n'
    '          const json = pm.response.json();\n'
    '          pm.expect(json).to.satisfy(function(j) {\n'
    '              return j.hasOwnProperty("email") || j.hasOwnProperty("username") || j.hasOwnProperty("id");\n'
    '          });\n'
    '      });\n'
    '\n'
    '      pm.test("Response time is under 2000ms", function () {\n'
    '          pm.expect(pm.response.responseTime).to.be.below(2000);\n'
    '      });\n'
    'order: 1000000000003000\n'
)

perfil_path = os.path.join(base, 'perfil.request.yaml')
with open(perfil_path, 'rb') as f:
    content = f.read().decode('utf-8')
new_content = content.replace('order: 1000000000003000\r\n', perfil_scripts).replace('order: 1000000000003000\n', perfil_scripts)
with open(perfil_path, 'wb') as f:
    f.write(new_content.encode('utf-8'))
print('perfil done')
