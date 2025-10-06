import sys
import csv
from PyQt6.QtWidgets import (
    QApplication, QWidget, QTableWidgetItem, QMessageBox, QAbstractItemView
)
from PyQt6 import uic


class Contacto:
    def __init__(self, nombre: str, telefono: str):
        self.nombre = nombre.strip()
        self.telefono = telefono.strip()

    def __str__(self):
        return f"{self.nombre} - {self.telefono}"


class NodoBST:
    def __init__(self, contacto: Contacto):
        self.contacto = contacto
        self.izq = None
        self.der = None


class AgendaBST:
    def __init__(self):
        self.raiz = None

    def insertar_contacto(self, contacto: Contacto):
        def _insertar(nodo, c):
            if nodo is None:
                return NodoBST(c)
            if c.nombre.lower() < nodo.contacto.nombre.lower():
                nodo.izq = _insertar(nodo.izq, c)
            elif c.nombre.lower() > nodo.contacto.nombre.lower():
                nodo.der = _insertar(nodo.der, c)
            else:
                nodo.contacto.telefono = c.telefono  
            return nodo

        self.raiz = _insertar(self.raiz, contacto)

    def buscar_contacto(self, nombre: str):
        def _buscar(nodo):
            if nodo is None:
                return None
            if nombre.lower() == nodo.contacto.nombre.lower():
                return nodo.contacto
            elif nombre.lower() < nodo.contacto.nombre.lower():
                return _buscar(nodo.izq)
            else:
                return _buscar(nodo.der)

        return _buscar(self.raiz)

    def eliminar_contacto(self, nombre: str):
        def _min(nodo):
            while nodo.izq:
                nodo = nodo.izq
            return nodo

        def _elim(nodo, nombre):
            if nodo is None:
                return None
            if nombre.lower() < nodo.contacto.nombre.lower():
                nodo.izq = _elim(nodo.izq, nombre)
            elif nombre.lower() > nodo.contacto.nombre.lower():
                nodo.der = _elim(nodo.der, nombre)
            else:
                
                if nodo.izq is None:
                    return nodo.der
                elif nodo.der is None:
                    return nodo.izq
                
                min_der = _min(nodo.der)
                nodo.contacto = min_der.contacto
                nodo.der = _elim(nodo.der, min_der.contacto.nombre)
            return nodo

        self.raiz = _elim(self.raiz, nombre)

    def listar_contactos_inorder(self):
        res = []

        def _inorder(nodo):
            if nodo:
                _inorder(nodo.izq)
                res.append(nodo.contacto)
                _inorder(nodo.der)

        _inorder(self.raiz)
        return res

    def listar_contactos_preorder(self):
        res = []

        def _preorder(nodo):
            if nodo:
                res.append(nodo.contacto)
                _preorder(nodo.izq)
                _preorder(nodo.der)

        _preorder(self.raiz)
        return res

    def listar_contactos_postorder(self):
        res = []

        def _postorder(nodo):
            if nodo:
                _postorder(nodo.izq)
                _postorder(nodo.der)
                res.append(nodo.contacto)

        _postorder(self.raiz)
        return res

    def exportar_csv(self, filename, contactos):
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["nombre", "telefono"])
            for c in contactos:
                writer.writerow([c.nombre, c.telefono])

    def exportar_inorder_csv(self):
        self.exportar_csv("agenda_ordenada.csv", self.listar_contactos_inorder())

    def exportar_preorder_csv(self):
        self.exportar_csv("agenda_preorder.csv", self.listar_contactos_preorder())

    def exportar_postorder_csv(self):
        self.exportar_csv("agenda_postorder.csv", self.listar_contactos_postorder())

    def busqueda_prefijo(self, prefijo):
        pref = prefijo.lower()
        res = []

        def _buscar_prefijo(nodo):
            if nodo:
                if nodo.contacto.nombre.lower().startswith(pref):
                    res.append(nodo.contacto)
              
                if pref <= nodo.contacto.nombre.lower():
                    _buscar_prefijo(nodo.izq)
                
                if pref >= nodo.contacto.nombre.lower()[:len(pref)]:
                    _buscar_prefijo(nodo.der)

        _buscar_prefijo(self.raiz)
        return res


class VentanaAgenda(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("agenda.ui", self)
        self.agenda = AgendaBST()
        self.cargar_csv_inicial()

       
        self.btn_insertar.clicked.connect(self.insertar_contacto)
        self.btn_buscar.clicked.connect(self.buscar_contacto)
        self.btn_eliminar.clicked.connect(self.eliminar_contacto)
        self.btn_listar.clicked.connect(self.listar_contactos)
        self.btn_exportar_inorder.clicked.connect(self.exportar_inorder)
        self.btn_exportar_preorder.clicked.connect(self.exportar_preorder)
        self.btn_exportar_postorder.clicked.connect(self.exportar_postorder)
        self.btn_mostrar_arbol.clicked.connect(self.mostrar_arbol_texto)
        self.btn_buscar_prefijo.clicked.connect(self.buscar_por_prefijo)

        self.tabla.setColumnCount(2)
        self.tabla.setHorizontalHeaderLabels(["Nombre", "Teléfono"])
        self.tabla.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def cargar_csv_inicial(self):
        try:
            with open("contacts.csv", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for fila in reader:
                    c = Contacto(fila["nombre"], fila["telefono"])
                    self.agenda.insertar_contacto(c)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo cargar contacts.csv: {e}")

    def insertar_contacto(self):
        nombre = self.nombre_input.text().strip()
        telefono = self.tel_input.text().strip()
        if not nombre or not telefono:
            QMessageBox.warning(self, "Error", "Ingrese nombre y teléfono")
            return
        c = Contacto(nombre, telefono)
        self.agenda.insertar_contacto(c)
        QMessageBox.information(self, "Éxito", f"Contacto '{nombre}' insertado/actualizado")
        self.limpiar_inputs()
        self.listar_contactos()

    def buscar_contacto(self):
        nombre = self.nombre_input.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "Ingrese nombre para buscar")
            return
        c = self.agenda.buscar_contacto(nombre)
        if c:
            self.mostrar_contactos([c])
        else:
            QMessageBox.information(self, "Resultado", f"No se encontró contacto con nombre '{nombre}'")

    def eliminar_contacto(self):
        nombre = self.nombre_input.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "Ingrese nombre para eliminar")
            return
        c = self.agenda.buscar_contacto(nombre)
        if c is None:
            QMessageBox.information(self, "Resultado", f"No existe contacto '{nombre}' para eliminar")
            return
        self.agenda.eliminar_contacto(nombre)
        QMessageBox.information(self, "Éxito", f"Contacto '{nombre}' eliminado")
        self.limpiar_inputs()
        self.listar_contactos()

    def listar_contactos(self):
        contactos = self.agenda.listar_contactos_inorder()
        self.mostrar_contactos(contactos)

    def mostrar_contactos(self, contactos):
        self.tabla.setRowCount(len(contactos))
        for fila, c in enumerate(contactos):
            self.tabla.setItem(fila, 0, QTableWidgetItem(c.nombre))
            self.tabla.setItem(fila, 1, QTableWidgetItem(c.telefono))

    def limpiar_inputs(self):
        self.nombre_input.clear()
        self.tel_input.clear()
        self.prefijo_input.clear()

    def exportar_inorder(self):
        self.agenda.exportar_inorder_csv()
        QMessageBox.information(self, "Exportar", "Exportado a agenda_ordenada.csv (inorder)")

    def exportar_preorder(self):
        self.agenda.exportar_preorder_csv()
        QMessageBox.information(self, "Exportar", "Exportado a agenda_preorder.csv (preorder)")

    def exportar_postorder(self):
        self.agenda.exportar_postorder_csv()
        QMessageBox.information(self, "Exportar", "Exportado a agenda_postorder.csv (postorder)")

    def mostrar_arbol_texto(self):
        lines = []

        def _preorder_text(nodo, nivel=0):
            if nodo is None:
                lines.append("    " * nivel + "<vacío>")
                return
            lines.append("    " * nivel + f"{nodo.contacto.nombre} ({nodo.contacto.telefono})")
            _preorder_text(nodo.izq, nivel + 1)
            _preorder_text(nodo.der, nivel + 1)

        _preorder_text(self.agenda.raiz)
        texto = "\n".join(lines)
        QMessageBox.information(self, "Estructura del Árbol (Preorder)", texto)

    def buscar_por_prefijo(self):
        prefijo = self.prefijo_input.text().strip()
        if not prefijo:
            QMessageBox.warning(self, "Error", "Ingrese prefijo para búsqueda")
            return
        resultados = self.agenda.busqueda_prefijo(prefijo)
        if resultados:
            self.mostrar_contactos(resultados)
        else:
            QMessageBox.information(self, "Resultado", "No se encontraron contactos con ese prefijo")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaAgenda()
    ventana.show()
    sys.exit(app.exec())