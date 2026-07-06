import os

# Rutas Base (Relativas al proyecto para pruebas, pueden cambiarse a C:\...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FOLDER = os.path.join(BASE_DIR, "Facturas_A_Procesar")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "Facturas_Procesadas")
UNRECOGNIZED_FOLDER = os.path.join(BASE_DIR, "Facturas_No_Reconocidas")

# Extensiones a monitorear
ALLOWED_EXTENSIONS = [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"]

# Diccionario de Proveedores y Expresiones Regulares
# Cada proveedor tiene una lista de palabras clave para identificarlo en el texto,
# y un patrón Regex para extraer el número de factura.
# El formato de número indicado es: Punto de Venta - Número (ej. 0001-12345678)
SUPPLIERS = {
    'Edenor': {
        "keywords": ['edenor', 'empresa distribuidora y comercializadora norte'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Metrogas': {
        "keywords": ['metrogas'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Mozzari': {
        "keywords": ['mozzari', '30-71637640-7', '30716376407', 'il sapore italiano', 'brie'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Oleiros SA': {
        "keywords": ['oleiros sa', 'oleiros', '30-70808111-2', '30708081112'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Roman Equipos S.R.L.': {
        "keywords": ['roman equipos s.r.l.', '30-71224791-2', '30712247912'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Caputo Emiliano Dante Y Caputo Flavio Andres S. Cap I Secc IV': {
        "keywords": ['caputo emiliano dante y caputo flavio andres s. cap i secc iv', 'caputo emiliano dante y caputo flavio andres', 'caputo emiliano dante', 'caputo flavio andres', '33-69652224-9', '33696522249', 'caputo emiliano dante y caputo flavio andres s. cap i iv', 'caputo emiliano', 'caputo flavio'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Mayer Gomez Veronica De Las Mercedes': {
        "keywords": ['mayer gomez veronica de las mercedes', 'mayer gomez veronica', 'las mercedes', '27-92395129-1', '27923951291'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Tarum S.R.L.': {
        "keywords": ['tarum s.r.l.', '30-71749677-5', '30717496775'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Id Group S.A.': {
        "keywords": ['id group s.a.', '30-70805310-0', '30708053100'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Bekir I S.R.L.': {
        "keywords": ['bekir i s.r.l.', '30-71526127-4', '30715261274'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Maxisistemas SRL': {
        "keywords": ['maxisistemas srl', 'maxisistemas', '30-70851699-2', '30708516992'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Grupo Concesionario Del Oeste SA': {
        "keywords": ['grupo concesionario del oeste sa', 'grupo concesionario del oeste', '30-66349851-3', '30663498513'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Delivery Hero E-commerce S. A.': {
        "keywords": ['delivery hero e-commerce s. a.', '30-71198576-6', '30711985766'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Autopistas Del Sol S A': {
        "keywords": ['autopistas del sol s a', '30-67723711-9', '30677237119'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Quinta La Perseverancia S R L': {
        "keywords": ['quinta la perseverancia s r l', '30-68556237-1', '30685562371'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Rodriguez Maria Valeria': {
        "keywords": ['rodriguez maria valeria', '27-21392134-2', '27213921342'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Supermercados El Abastecedor SA': {
        "keywords": ['supermercados el abastecedor sa', 'supermercados el abastecedor', '30-71495614-7', '30714956147'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Verisure Argentina Monitoreo De Alarmas SA': {
        "keywords": ['verisure argentina monitoreo de alarmas sa', 'verisure argentina', 'verisure argentina monitoreo', 'alarmas', '33-71630774-9', '33716307749'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Sociedad Ley 19550 Cap I Seccion IV De Staropoli Pablo Y Bertoia Franco': {
        "keywords": ['sociedad ley 19550 cap i seccion iv de staropoli pablo y bertoia franco', 'de staropoli pablo y bertoia franco', 'staropoli pablo', 'bertoia franco', '30-71633841-6', '30716338416'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Deheza Sociedad Anonima Industrial Comercial Financiera Inmobiliaria': {
        "keywords": ['deheza sociedad anonima industrial comercial financiera inmobiliaria', 'deheza', '30-51618667-0', '30516186670'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Sasem Logics S.R.L.': {
        "keywords": ['sasem logics s.r.l.', '30-71218120-2', '30712181202'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Frio Interlogistica Sur SA': {
        "keywords": ['frio interlogistica sur sa', 'frio interlogistica sur', '30-71069305-2', '30710693052'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Rojas Manuela': {
        "keywords": ['rojas manuela', '27-27217076-8', '27272170768'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Romano Hector Esteban': {
        "keywords": ['romano hector esteban', '20-38705422-8', '20387054228'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Villares Sociedad Anonima Comercial': {
        "keywords": ['villares sociedad anonima comercial', 'villares', '30-53785301-4', '30537853014'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Podic SA': {
        "keywords": ['podic sa', 'podic', '30-61164439-2', '30611644392'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Weler S.A.': {
        "keywords": ['weler s.a.', '30-71679140-4', '30716791404'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'S3ba S.A.': {
        "keywords": ['s3ba s.a.', '30-71844205-9', '30718442059'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Operadora De Estaciones De Servicios SA': {
        "keywords": ['operadora de estaciones de servicios sa', 'operadora', 'estaciones', 'servicios', '30-67877449-5', '30678774495'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Villca Apaza Walter Diego': {
        "keywords": ['villca apaza walter diego', '20-29330172-8', '20293301728'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Logistica La Serenisima SA': {
        "keywords": ['logistica la serenisima sa', 'logistica la serenisima', '30-70721038-5', '30707210385'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Jaureguy Sociedad Anonima Comercial E Industrial Y Agropecuaria': {
        "keywords": ['jaureguy sociedad anonima comercial e industrial y agropecuaria', 'jaureguy', 'jaureguy e industrial', 'agropecuaria', '30-52101843-3', '30521018433'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Coca Cola Femsa De Buenos Aires S A': {
        "keywords": ['coca cola femsa de buenos aires s a', 'coca cola femsa', 'buenos aires s a', '30-52539008-6', '30525390086'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Shoijet Yuval': {
        "keywords": ['shoijet yuval', '20-47005430-2', '20470054302'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Coto Centro Integral De Comercializacion Sociedad Anonima': {
        "keywords": ['coto centro integral de comercializacion sociedad anonima', 'coto', 'coto centro integral', 'comercializacion', '30-54808315-6', '30548083156'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Cencosud S A': {
        "keywords": ['cencosud s a', '30-59036076-3', '30590360763'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Pl3m S.A.': {
        "keywords": ['pl3m s.a.', '30-71127123-2', '30711271232'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Fadefil S.A.': {
        "keywords": ['fadefil s.a.', '30-71295020-6', '30712950206'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Linkedstore Argentina S.R.L.': {
        "keywords": ['linkedstore argentina s.r.l.', '30-71201935-9', '30712019359'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Aversa Carlos Francisco': {
        "keywords": ['aversa carlos francisco', '20-08443853-8', '20084438538'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Cosentino Mariano Alejandro': {
        "keywords": ['cosentino mariano alejandro', '20-18505724-1', '20185057241'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Frigorifico La Octava S A': {
        "keywords": ['frigorifico la octava s a', '30-65199259-8', '30651992598'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Quimica Moron SRL': {
        "keywords": ['quimica moron srl', 'quimica moron', '30-70919002-0', '30709190020'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Marchionni Damian Leonardo': {
        "keywords": ['marchionni damian leonardo', '20-24515871-9', '20245158719'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Martinez Javier Alberto': {
        "keywords": ['martinez javier alberto', '20-30800862-3', '20308008623'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Ypf Gas Sociedad Anonima': {
        "keywords": ['ypf gas sociedad anonima', 'ypf gas', '30-51548847-9', '30515488479'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Filieres S R L': {
        "keywords": ['filieres s r l', '30-70739869-4', '30707398694'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'La Nacion S. A.': {
        "keywords": ['la nacion s. a.', '30-50008962-4', '30500089624'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Cianciaruso Carlos Eugenio': {
        "keywords": ['cianciaruso carlos eugenio', '20-16037082-4', '20160370824'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Tapalque Alimentos SA': {
        "keywords": ['tapalque alimentos sa', 'tapalque alimentos', '33-58131161-9', '33581311619'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Telefonica Moviles Argentina Sociedad Anonima': {
        "keywords": ['telefonica moviles argentina sociedad anonima', '30-67881435-7', '30678814357'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Route Green S.R.L.': {
        "keywords": ['route green s.r.l.', '30-71566458-1', '30715664581'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Distribuidora Armando Hernando Simple Asociacion': {
        "keywords": ['distribuidora armando hernando simple asociacion', '30-71775774-9', '30717757749'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Distribuidora El Criollo SRL': {
        "keywords": ['distribuidora el criollo srl', 'distribuidora el criollo', '30-70887901-7', '30708879017'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Nestle Argentina S A': {
        "keywords": ['nestle argentina s a', '30-54676404-0', '30546764040'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Pastorino Ariel Hernan': {
        "keywords": ['pastorino ariel hernan', '20-28033675-1', '20280336751'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Pina Pesca Sociedad Anonima': {
        "keywords": ['pina pesca sociedad anonima', 'pina pesca', '30-71222415-7', '30712224157'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Las Dinas S R L': {
        "keywords": ['las dinas s r l', '33-60695684-9', '33606956849'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Central Oeste Leloir Sociedad En Comandita Simple': {
        "keywords": ['central oeste leloir sociedad en comandita simple', '30-70854976-9', '30708549769'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Felicita Hnos Wgt S. R. L.': {
        "keywords": ['felicita hnos wgt s. r. l.', '30-71829378-9', '30718293789'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Maree': {
        "keywords": ['maree', '30-71715308-8', '30717153088'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'La Estrella De Galicia S C A': {
        "keywords": ['la estrella de galicia s c a', 'la estrella de galicia a', 'la estrella', 'galicia a', '30-50548626-5', '30505486265'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Parsom S.A': {
        "keywords": ['parsom s.a', '30-70983262-6', '30709832626'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Reginald Lee S A': {
        "keywords": ['reginald lee s a', '30-53662310-4', '30536623104'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Ortiz Pablo Javier': {
        "keywords": ['ortiz pablo javier', '20-24754218-4', '20247542184'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Viva Hernan Gonzalo': {
        "keywords": ['viva hernan gonzalo', '20-24914663-4', '20249146634'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'De Los Santos Romero Miriam Yanet': {
        "keywords": ['de los santos romero miriam yanet', '27-94976131-8', '27949761318'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Central 23 S.a.s.': {
        "keywords": ['central 23 s.a.s.', 'central 23 s.', '30-71581156-8', '30715811568'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Lavanderia Febo SRL': {
        "keywords": ['lavanderia febo srl', 'lavanderia febo', '30-70786266-8', '30707862668'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Autopistas De Buenos Aires (aubasa) SA S. A.': {
        "keywords": ['autopistas de buenos aires (aubasa) sa s. a.', 'autopistas (aubasa) s. a.', 'autopistas', 'buenos aires (aubasa) s. a.', '30-71411283-6', '30714112836'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Coordinacion Ecologica Area Metropolitana Sociedad Del Estado': {
        "keywords": ['coordinacion ecologica area metropolitana sociedad del estado', 'coordinacion ecologica area metropolitana', '30-57720719-0', '30577207190'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Saitta Marcelo Daniel': {
        "keywords": ['saitta marcelo daniel', '20-27419539-9', '20274195399'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Viscardi Martin Ramon': {
        "keywords": ['viscardi martin ramon', '20-23945714-3', '20239457143'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Autopistas Urbanas S. A.': {
        "keywords": ['autopistas urbanas s. a.', '30-57487647-4', '30574876474'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'S A Miguel Campodonico Ltda': {
        "keywords": ['s a miguel campodonico ltda', 'miguel campodonico', '33-52780130-9', '33527801309'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Cabaña Piedras Blancas S R L': {
        "keywords": ['cabaña piedras blancas s r l', '30-66513397-0', '30665133970'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Lopez Leandro Martin': {
        "keywords": ['lopez leandro martin', '20-35363940-5', '20353639405'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Paradela Mercedes Soledad': {
        "keywords": ['paradela mercedes soledad', '27-26725336-1', '27267253361'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Rolando Alfredo Nelson': {
        "keywords": ['rolando alfredo nelson', '20-04595129-5', '20045951295'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Pacrisva Sociedad Anonima': {
        "keywords": ['pacrisva sociedad anonima', 'pacrisva', '30-62884156-6', '30628841566'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Diaz Elsa Angelica': {
        "keywords": ['diaz elsa angelica', '27-05631583-2', '27056315832'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Burnet Michaut Gaston Kurt': {
        "keywords": ['burnet michaut gaston kurt', '20-23572390-6', '20235723906'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Arte Grafico Editorial Argentino S. A.': {
        "keywords": ['arte grafico editorial argentino s. a.', '30-50012415-2', '30500124152'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Lodiser SA': {
        "keywords": ['lodiser sa', 'lodiser', '30-70705980-6', '30707059806'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Occ Professional SRL': {
        "keywords": ['occ professional srl', 'occ professional', '30-71554854-9', '30715548549'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Tonna S A': {
        "keywords": ['tonna s a', '30-70210242-8', '30702102428'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Roberto O Rodofeli Y Cia S R L': {
        "keywords": ['roberto o rodofeli y cia s r l', 'roberto o rodofeli', 'cia s r l', '30-54752995-9', '30547529959'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Cassini Martin': {
        "keywords": ['cassini martin', '20-27182205-8', '20271822058'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Grupo Babystore S.R.L.': {
        "keywords": ['grupo babystore s.r.l.', '30-71184733-9', '30711847339'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Graphic S.A.': {
        "keywords": ['graphic s.a.', '30-70957312-4', '30709573124'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Asensio Sistemas S A': {
        "keywords": ['asensio sistemas s a', '30-70359813-3', '30703598133'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Benitez German Gabriel': {
        "keywords": ['benitez german gabriel', '20-39436496-8', '20394364968'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'La Mision Tacaagle S.A.': {
        "keywords": ['la mision tacaagle s.a.', '30-70882889-7', '30708828897'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Prolait SRL': {
        "keywords": ['prolait srl', 'prolait', '30-71566489-1', '30715664891'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Moñas SA': {
        "keywords": ['moñas sa', 'moñas', '30-71717553-7', '30717175537'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Amx Argentina Sociedad Anonima': {
        "keywords": ['amx argentina sociedad anonima', 'amx argentina', '30-66328849-7', '30663288497'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Oyhanarte Guillermo Edgardo': {
        "keywords": ['oyhanarte guillermo edgardo', '20-16919453-0', '20169194530'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Fernandez Gustavo Osvaldo': {
        "keywords": ['fernandez gustavo osvaldo', '20-25866524-5', '20258665245'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Haberkorn Elio Fernando': {
        "keywords": ['haberkorn elio fernando', '20-13428298-4', '20134282984'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Nario Leandro Guillermo': {
        "keywords": ['nario leandro guillermo', '20-32536342-9', '20325363429'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Grasso Maria': {
        "keywords": ['grasso maria', '27-93236958-9', '27932369589'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Telecom Argentina Sociedad Anonima': {
        "keywords": ['telecom argentina sociedad anonima', '30-63945373-8', '30639453738'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Noriega Esparza Cristo Rene': {
        "keywords": ['noriega esparza cristo rene', '20-94039638-8', '20940396388'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Girasoles Hernan Osvaldo': {
        "keywords": ['girasoles hernan osvaldo', '20-35537536-7', '20355375367'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Lopez Figueroa Patricio': {
        "keywords": ['lopez figueroa patricio', '20-31352369-2', '20313523692'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Cooperativa Obrera Limitada De Consumo Y Vivienda': {
        "keywords": ['cooperativa obrera limitada de consumo y vivienda', 'cooperativa obrera', 'consumo', 'vivienda', '30-52570593-1', '30525705931'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Mercadolibre S.R.L.': {
        "keywords": ['mercadolibre s.r.l.', '30-70308853-4', '30703088534'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Bodegas Salentein S. A.': {
        "keywords": ['bodegas salentein s. a.', '30-69759871-1', '30697598711'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Ledesma Luciano Ariel': {
        "keywords": ['ledesma luciano ariel', '20-23769949-2', '20237699492'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Chlaula Lisandro Luis': {
        "keywords": ['chlaula lisandro luis', '20-23431573-1', '20234315731'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Limardo Gabriel': {
        "keywords": ['limardo gabriel', '20-18440920-9', '20184409209'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Lezama Energia SA': {
        "keywords": ['lezama energia sa', 'lezama energia', '30-71681332-7', '30716813327'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Figueroa Elizabeth Carla': {
        "keywords": ['figueroa elizabeth carla', '27-26074807-1', '27260748071'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Laser House S.A.': {
        "keywords": ['laser house s.a.', '30-70854065-6', '30708540656'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Teknium S.r.l': {
        "keywords": ['teknium s.r.l', '33-71868916-9', '33718689169'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'D F Megafrio S R L': {
        "keywords": ['d f megafrio s r l', '30-69255874-6', '30692558746'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Apxer SRL': {
        "keywords": ['apxer srl', 'apxer', '30-70913043-5', '30709130435'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Nativa Libros SRL': {
        "keywords": ['nativa libros srl', 'nativa libros', '30-71528078-3', '30715280783'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Gergal SA': {
        "keywords": ['gergal sa', 'gergal', '30-63265369-3', '30632653693'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Gastrofactory On Line S.A.': {
        "keywords": ['gastrofactory on line s.a.', '30-71498189-3', '30714981893'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Alyser SA': {
        "keywords": ['alyser sa', 'alyser', '30-70776023-7', '30707760237'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Bengardino Jonathan Gaston': {
        "keywords": ['bengardino jonathan gaston', '20-33936305-7', '20339363057'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Horeca Srl.': {
        "keywords": ['horeca srl.', 'horeca .', '30-71209619-1', '30712096191'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Le-fit Food S.a.s.': {
        "keywords": ['le-fit food s.a.s.', 'le-fit food s.', '30-71652295-0', '30716522950'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Gatti Andrea Myriam Lorena': {
        "keywords": ['gatti andrea myriam lorena', '23-20420641-4', '23204206414'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Suarez Yesica': {
        "keywords": ['suarez yesica', '27-33149584-6', '27331495846'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Compañia Exportadora SRL': {
        "keywords": ['compañia exportadora srl', 'compañia exportadora', '33-70787660-9', '33707876609'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Silva Hernan Mauricio': {
        "keywords": ['silva hernan mauricio', '20-27083406-0', '20270834060'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Gutierrez Fernando Nicolas': {
        "keywords": ['gutierrez fernando nicolas', '20-29670654-0', '20296706540'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Duarte Rocio Veronica': {
        "keywords": ['duarte rocio veronica', '27-24212054-5', '27242120545'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Mieles Cor Pam SRL': {
        "keywords": ['mieles cor pam srl', 'mieles cor pam', '30-70787970-6', '30707879706'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Campili Nicolas Adrian': {
        "keywords": ['campili nicolas adrian', '20-30991016-9', '20309910169'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Soverna Alicia Beatriz': {
        "keywords": ['soverna alicia beatriz', '27-11203322-5', '27112033225'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Dia Argentina S A': {
        "keywords": ['dia argentina s a', '30-68584975-1', '30685849751'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Sabo Smart SRL': {
        "keywords": ['sabo smart srl', 'sabo smart', '30-71760806-9', '30717608069'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Andrade Leandro Ezequiel': {
        "keywords": ['andrade leandro ezequiel', '20-26934445-9', '20269344459'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Hauff Martin Sebastian': {
        "keywords": ['hauff martin sebastian', '20-30163799-4', '20301637994'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Torikos S.a.s.': {
        "keywords": ['torikos s.a.s.', 'torikos s.', '30-71608649-2', '30716086492'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Seacom SRL': {
        "keywords": ['seacom srl', 'seacom', '30-71069056-8', '30710690568'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Fp Paper Bags S.R.L.': {
        "keywords": ['fp paper bags s.r.l.', '30-71084111-6', '30710841116'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Di Sabatino Elio Demian': {
        "keywords": ['di sabatino elio demian', '20-25765841-5', '20257658415'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Antedoro Jeremias Fabian': {
        "keywords": ['antedoro jeremias fabian', '20-35727588-2', '20357275882'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Pinamar Higiene Institucional S.R.L.': {
        "keywords": ['pinamar higiene institucional s.r.l.', '30-71784729-2', '30717847292'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Supermercados Mayoristas Makro S. A.': {
        "keywords": ['supermercados mayoristas makro s. a.', '30-58962149-9', '30589621499'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'La Boya Del Bajo S.R.L.': {
        "keywords": ['la boya del bajo s.r.l.', '30-71696362-0', '30716963620'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Carcaterra Alejandro Federico': {
        "keywords": ['carcaterra alejandro federico', '20-16622502-8', '20166225028'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Empresa Distribucion Norte S.R.L.': {
        "keywords": ['empresa distribucion norte s.r.l.', '30-71437958-1', '30714379581'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Volf S.A.': {
        "keywords": ['volf s.a.', '30-50436387-9', '30504363879'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Devincenzi Jeremias Emiliano': {
        "keywords": ['devincenzi jeremias emiliano', '20-29247001-1', '20292470011'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Peinado Martin Guillermo': {
        "keywords": ['peinado martin guillermo', '20-24964018-3', '20249640183'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Colucci Equipamiento S.A.': {
        "keywords": ['colucci equipamiento s.a.', '30-71699309-0', '30716993090'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Rincon Dario Javier': {
        "keywords": ['rincon dario javier', '20-31349218-5', '20313492185'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Malmsten Maria Eugenia': {
        "keywords": ['malmsten maria eugenia', '27-30603564-4', '27306035644'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Sgaramello Daniela Evelyn': {
        "keywords": ['sgaramello daniela evelyn', '27-36078837-2', '27360788372'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Despegar Com Ar SA': {
        "keywords": ['despegar com ar sa', 'despegar com ar', '30-70130711-5', '30701307115'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Sant Energy S.A.': {
        "keywords": ['sant energy s.a.', '30-71800414-0', '30718004140'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Degreen S A': {
        "keywords": ['degreen s a', '30-69338021-5', '30693380215'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Cultivate La Buena Vida S.A.': {
        "keywords": ['cultivate la buena vida s.a.', '30-71504024-3', '30715040243'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Nicknat S.R.L.': {
        "keywords": ['nicknat s.r.l.', '30-71557795-6', '30715577956'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Kaprielian Brenda Sofia': {
        "keywords": ['kaprielian brenda sofia', '27-27680681-0', '27276806810'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Shen Wei Ting': {
        "keywords": ['shen wei ting', '20-93884199-4', '20938841994'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Speed Business S. A.': {
        "keywords": ['speed business s. a.', '30-68697835-0', '30686978350'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Fernandez Maria Del Carmen': {
        "keywords": ['fernandez maria del carmen', '23-17918239-4', '23179182394'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'El Nuevo Emporio SA': {
        "keywords": ['el nuevo emporio sa', 'el nuevo emporio', '33-70703773-9', '33707037739'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Corredores Viales Sociedad Anonima': {
        "keywords": ['corredores viales sociedad anonima', 'corredores viales', '30-71580481-2', '30715804812'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Garcea Ignacio Leonel': {
        "keywords": ['garcea ignacio leonel', '20-31915632-2', '20319156322'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Servinorte S A': {
        "keywords": ['servinorte s a', '30-64572255-4', '30645722554'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
    'Crespo Lucas Agustin': {
        "keywords": ['crespo lucas agustin', '20-43103701-8', '20431037018'],
        "invoice_regex": r"(\d{4,5}\s*-\s*\d{8})"
    },
}
