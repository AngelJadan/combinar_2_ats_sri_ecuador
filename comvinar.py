import xml.etree.ElementTree as ET
from collections import defaultdict
import copy


tree1 = ET.parse('Nombre de primer archivo xml.xml')
tree2 = ET.parse('Nombre de segundo archivo xml.xml')
xml_name = "ats_generado.xml"
tipo_emision = "E"
total_venta = 0
# Cargar XMLs

root1 = tree1.getroot()
root2 = tree2.getroot()

# Crear estructura base
iva = ET.Element("iva")

# Datos fijos del encabezado
ET.SubElement(iva, "TipoIDInformante").text = "R"
ET.SubElement(iva, "IdInformante").text = "Ruc de la compañia"
ET.SubElement(iva, "razonSocial").text = "Razon social de la compañia"
ET.SubElement(iva, "Anio").text = "Año a reportarse" #2025
ET.SubElement(iva, "Mes").text = "mes a reportarse" #01, 02, etc.
ET.SubElement(iva, "numEstabRuc").text = "001" #Se actualizará despues
ET.SubElement(iva, "totalVentas").text = "0.00" #Se actualizará despues
ET.SubElement(iva, "codigoOperativo").text = "IVA"

# Combinar detalleCompras
compras = ET.SubElement(iva, "compras")
for detalle in root1.findall(".//detalleCompras") + root2.findall(".//detalleCompras"):
    compras.append(copy.deepcopy(detalle))

# Combinar detalleVentas sumando por idCliente
ventas = ET.SubElement(iva, "ventas")
#detalle_ventas = ET.SubElement(ventas, "detalleVentas")

clientes_dict = defaultdict(lambda: None)

def get_float(elem, tag):
    value = elem.findtext(tag)
    return float(value) if value else 0.0

for venta in root1.findall(".//detalleVentas") + root2.findall(".//detalleVentas"):
    
    id_cliente = venta.findtext("idCliente")
    if not id_cliente:
        continue

    if venta.find("tipoEmision") is not None:
        venta.find("tipoEmision").text = tipo_emision
    
    if tipo_emision=="F":
        total_venta += (
            get_float(venta, "baseNoGraIva") +
            get_float(venta, "baseImponible") +
            get_float(venta, "baseImpGrav")
        )

    if clientes_dict[id_cliente] is None:
        clientes_dict[id_cliente] = copy.deepcopy(venta)
    else:
        actual = clientes_dict[id_cliente]
        # Sumar los campos numéricos según tu necesidad
        for tag in ["numeroComprobantes","baseNoGraIva", "baseImponible", "baseImpGrav","montoIva","montoIce","valorRetIva","valorRetRenta"]:
            actual_value = get_float(actual, tag)
            nuevo_valor = get_float(venta, tag)
            if actual.find(tag)!=None:
                if tag=="numeroComprobantes":
                    actual.find(tag).text = f"{actual_value + nuevo_valor:.0f}"
                else:
                    actual.find(tag).text = f"{actual_value + nuevo_valor:.2f}"
            
                
    
# Agregar ventas únicas
for venta in clientes_dict.values():
    ventas.append(venta)


def get_float(elem, tag):
    value = elem.findtext(tag)
    return float(value) if value else 0.0

totales_por_estab = []
# Función para procesar un archivo con su codEstab forzado
def procesar_archivo(root, cod_estab_forzado):
    total_est = 0
    if tipo_emision=="F":
        for venta in root.findall(".//detalleVentas"):
            total_est += (get_float(venta, "baseNoGraIva")+
                            get_float(venta, "baseImponible")+
                            get_float(venta, "baseImpGrav"))
    totales_por_estab.append({"cod_estab":cod_estab_forzado,"totales":total_est})

# Procesar ambos archivos con su codEstab respectivo
if tipo_emision=="F":
    procesar_archivo(root1, "001")
    procesar_archivo(root2, "002")
    # Agregar ventasEstablecimiento dinámico
    ventas_establecimiento = ET.SubElement(iva, "ventasEstablecimiento")
    for establecimiento in totales_por_estab:
        venta_est = ET.SubElement(ventas_establecimiento, "ventaEst")
        ET.SubElement(venta_est, "codEstab").text = establecimiento['cod_estab']
        ET.SubElement(venta_est, "ventasEstab").text = f"{establecimiento['totales']:.2f}"
        ET.SubElement(venta_est, "ivaComp").text = "0.00"
    
    iva.find("numEstabRuc").text = f"{str(len(totales_por_estab)).zfill(3)}"
else:
    ventas_establecimiento = ET.SubElement(iva, "ventasEstablecimiento")
    venta_est = ET.SubElement(ventas_establecimiento, "ventaEst")
    ET.SubElement(venta_est, "codEstab").text = "001"
    ET.SubElement(venta_est, "ventasEstab").text = "0.00"
    ET.SubElement(venta_est, "ivaComp").text = "0.00"

if tipo_emision=="F":
    iva.find("totalVentas").text = f"{total_venta:.2f}"



#anulados = ET.SubElement(iva, "anulados")
#detalle_anulados = ET.SubElement(anulados, "detalleAnulados")
#for anulado in root1.findall(".//detalleAnulados") + root2.findall(".//detalleAnulados"):
#    detalle_anulados.append(copy.deepcopy(anulado))

# Guardar nuevo XML
tree_out = ET.ElementTree(iva)
tree_out.write(xml_name, encoding="utf-8", xml_declaration=True)
print("terminado.")
