#!/usr/bin/env python

# Copyright (C) 2014 Olivier Azeau <xxxcells@azeau.com>
# 
# This file is part of SixCells.
# 
# SixCells is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# SixCells is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with SixCells.  If not, see <http://www.gnu.org/licenses/>.


import io
import re

import common
from common import *

from qt.core import QUrl
from qt.widgets import QApplication, QMainWindow, QMessageBox, QHBoxLayout, QVBoxLayout, QDialog, QPushButton, QLineEdit, QDialogButtonBox, QLabel, QListWidget, QListWidgetItem, QProgressBar
from qt.network import QNetworkAccessManager, QNetworkRequest


class Cell(common.Cell):
  @property
  def value(self):
    pass
  
  @value.setter
  def value(self, value):
    pass


class Column(common.Column):
  @property
  def value(self):
    pass
  
  @value.setter
  def value(self, value):
    pass
  
  @property
  def together(self):
    pass
  
  @value.setter
  def together(self, value):
    pass



class Dialog(QDialog):
    current_url = "http://"
    current_content = ""
            
    def __init__(self,parent=None):
      QDialog.__init__(self,parent)
      
      self.network_access = QNetworkAccessManager()
      
      # TODO : a better regex that does not need <code></code> tags
      self.level_regex = re.compile('<code>(Hexcells level v1.*?)</code>', re.IGNORECASE|re.MULTILINE)

      self.setWindowTitle("Open from web page")
      self.setModal(True)
      layout = QVBoxLayout()
      self.setLayout(layout)
        
      url_selection = QHBoxLayout()
      url_selection.addWidget(QLabel("URL:"))
      self.url_field = QLineEdit(Dialog.current_url)
      self.url_field.setMinimumWidth(400)
      url_selection.addWidget(self.url_field)
      fetch_button = QPushButton("Fetch")
      fetch_button.clicked.connect(self.fetch_url)
      url_selection.addWidget(fetch_button)  
      layout.addLayout(url_selection)
      
      self.fetch_in_progress = QProgressBar()
      layout.addWidget(self.fetch_in_progress)
      
      def level_selection_changed():
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(True)
      self.levels = QListWidget()
      layout.addWidget(self.levels)
      self.levels.itemSelectionChanged.connect(level_selection_changed)
      
      def rejected():
        self.selected_level_file = None
        self.reject()
      def accepted():
        self.selected_level_file = self.levels.selectedItems()[0].data(qt.UserRole)
        self.accept()
      self.button_box = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
      self.button_box.rejected.connect(rejected)
      self.button_box.accepted.connect(accepted)
      self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
      layout.addWidget(self.button_box)
      
      self.webpage_content = Dialog.current_content
      self.find_levels_in_content()
    
    def fetch_url(self):
      Dialog.current_url = self.url_field.text()
      self.reply = self.network_access.get(QNetworkRequest(QUrl(Dialog.current_url)))
      def load_in_progress(current,maximum):
        self.fetch_in_progress.setMaximum(maximum)
        self.fetch_in_progress.setValue(current)
      load_in_progress(0,1)
      self.reply.downloadProgress.connect(lambda received, total: load_in_progress(received,total))
      self.reply.finished.connect(self.fetch_ok)
      self.reply.error.connect(self.fetch_error)
      
    def fetch_ok(self):
      self.levels.clear()
      self.webpage_content = self.get_webpage_content().replace("\n","\r")
      self.find_levels_in_content()
      
    def find_levels_in_content(self):
      Dialog.current_content = self.webpage_content
      all_matches = self.level_regex.finditer(self.webpage_content)
      for match in all_matches:
        self.add_level(match.group(1).replace("\r","\n"))
      self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
      
    def get_webpage_content(self):
      # TODO : a proper conversion to text using the webpage encoding -- currently we just directly use the webpage bytes
      bytes = self.reply.readAll()
      return bytes.data()
      
    def add_level(self,content):
      f = io.BytesIO()
      f.write(content)
      f.seek(0)
      scene = Scene()
      try:
        load_hexcells(f, scene, Cell, Column)
      except ValueError as e:
        return
      level = QListWidgetItem(scene.title+" (Author:"+scene.author+")")
      f.seek(0)
      level.setData(qt.UserRole,f)
      self.levels.addItem(level)
      
    def fetch_error(self):
      self.fetch_in_progress.reset()
      QMessageBox.critical(self, "Error", "Cannot fetch web page")


############################################################################
# Code below is only for testing purpose of the webpage fetching dialog
# It is not used in the full program

class TestDialog(Dialog):
    
    def __init__(self,parent=None):
      Dialog.__init__(self,parent)
      self.url_field.setText("http://www.reddit.com/r/hexcellslevels/comments/2h3l6f/level_pack_global_challenges_mediumhard/")
      
      self.plaintext_content = qt.widgets.QPlainTextEdit()
      self.layout().addWidget(self.plaintext_content)
      
      def fill_levels():
        self.webpage_content = """abcd<code>Hexcells level v1
	Test1
	oaz
	
	Do you need help?
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	................................O+................................
	..............................x...x...............................
	................................x.................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................</code>
	abcdef<code>Hexcells level v1
	Test2
	oaz
	
	Do you need help?
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	................................O+................................
	..............................x...x...............................
	................................x.................................
	..............................x...................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................
	..................................................................</code>""".replace("\n","\r")
        self.find_levels_in_content()
      
      fill_levels_button = QPushButton("Simulate Fill Levels")
      fill_levels_button.clicked.connect(fill_levels)
      self.layout().addWidget(fill_levels_button)
      
    def fetch_ok(self):
      super(TestDialog,self).fetch_ok()
      self.plaintext_content.setPlainText(self.webpage_content)

if __name__=='__main__':
  app = QApplication(sys.argv)
  dialog = TestDialog()
  if dialog.exec_() == QDialog.Accepted:
    QMessageBox.information(None, "Selected level", dialog.selected_level_file.read())
  else:
    QMessageBox.information(None, "Selected level", "NONE")
  

