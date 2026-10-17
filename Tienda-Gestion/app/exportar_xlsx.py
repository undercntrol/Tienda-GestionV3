"""Crea archivos .xlsx sin librerías externas (solo la librería estándar).

Un .xlsx es un ZIP con archivos XML. Escribirlo a mano evita tener que
instalar openpyxl en el computador de la tienda. La primera fila de cada
hoja sale como encabezado (negrita, blanco sobre verde).
"""

from __future__ import annotations

import zipfile
from xml.sax.saxutils import escape as _esc_xml


def _col_letra(num: int) -> str:
    letras = ""
    while num:
        num, resto = divmod(num - 1, 26)
        letras = chr(65 + resto) + letras
    return letras


def _hoja_xml(filas) -> str:
    partes = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
              '<sheetData>']
    for i, fila in enumerate(filas, 1):
        partes.append(f'<row r="{i}">')
        for j, v in enumerate(fila, 1):
            ref = f"{_col_letra(j)}{i}"
            s = ' s="1"' if i == 1 else ""
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                partes.append(f'<c r="{ref}"{s}><v>{v}</v></c>')
            else:
                partes.append(f'<c r="{ref}"{s} t="inlineStr"><is>'
                              f'<t xml:space="preserve">{_esc_xml(str(v))}</t></is></c>')
        partes.append('</row>')
    partes.append('</sheetData></worksheet>')
    return "".join(partes)


def exportar_xlsx(ruta, hojas) -> None:
    """hojas = [(nombre_hoja, [[fila1...], [fila2...]]), ...]"""
    n = len(hojas)
    tipos = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
             '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
             '<Default Extension="xml" ContentType="application/xml"/>'
             '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
             '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
             + "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" '
                       'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                       for i in range(1, n + 1))
             + '</Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            '</Relationships>')
    libro = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
             'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
             + "".join(f'<sheet name="{_esc_xml(nombre)}" sheetId="{i}" r:id="rId{i}"/>'
                       for i, (nombre, _f) in enumerate(hojas, 1))
             + '</sheets></workbook>')
    libro_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                  '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                  + "".join(f'<Relationship Id="rId{i}" '
                            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" '
                            f'Target="worksheets/sheet{i}.xml"/>' for i in range(1, n + 1))
                  + f'<Relationship Id="rId{n + 1}" '
                    'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" '
                    'Target="styles.xml"/>'
                  + '</Relationships>')
    estilos = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
               '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
               '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font>'
               '<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font></fonts>'
               '<fills count="3"><fill><patternFill patternType="none"/></fill>'
               '<fill><patternFill patternType="gray125"/></fill>'
               '<fill><patternFill patternType="solid"><fgColor rgb="FF0A7A0A"/><bgColor indexed="64"/></patternFill></fill></fills>'
               '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
               '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
               '<cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
               '<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/></cellXfs>'
               '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
               '</styleSheet>')

    with zipfile.ZipFile(ruta, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", tipos)
        z.writestr("_rels/.rels", rels)
        z.writestr("xl/workbook.xml", libro)
        z.writestr("xl/_rels/workbook.xml.rels", libro_rels)
        z.writestr("xl/styles.xml", estilos)
        for i, (_nombre, filas) in enumerate(hojas, 1):
            z.writestr(f"xl/worksheets/sheet{i}.xml", _hoja_xml(filas))
