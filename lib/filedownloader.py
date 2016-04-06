#!/usr/bin/env python
# -*- coding:utf-8 -*-

from gi.repository import Gtk, Gdk, GObject
from threading import Thread
import urllib.request
import time
import sys
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.parse import unquote_plus
import lxml
import lxml.html
import os
import glob
from os.path import basename
import threading
import queue

GObject.threads_init()

NUM_THREADS = 10

def name_file(imgUrl):
	fileName = unquote_plus(unquote_plus(unquote_plus(basename(imgUrl))))
	if os.path.exists(fileName):
		base,ext = os.path.splitext(fileName)
		print(fileName)
		print(base+'*'+ext)
		nfiles = len(glob.glob(base+'*'+ext))
		fileName = base+'_'+str(nfiles)+ext
	return fileName

def get_file_urls(mainUrl,extension):
	uniFileUrls = []
	if not mainUrl.lower().startswith('http://') and not mainUrl.lower().startswith('https://'):
		mainUrl = 'http://%s'%mainUrl
	print('Downloading from %s...'%mainUrl)
	if extension.startswith('*'):
		extension = extension[1:]
	if not extension.startswith('.'):
		extension = '.' + extension
	req = urllib.request.Request(
		mainUrl, 
		data=None, 
		headers={
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
		}
	)
	urlContent = urllib.request.urlopen(req).read().decode('utf-8')
	html = lxml.html.fromstring(urlContent)	
	urls = html.xpath('//a/@href')
	for url in urls:
		if url.endswith(extension):
			url = urljoin(mainUrl,url)
			if url not in uniFileUrls:
				uniFileUrls.append(url)
	return uniFileUrls

class Worker(GObject.GObject,threading.Thread):
	__gsignals__ = {
		'downloaded':(GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,(object,)),
		}
	
	def __init__(self,cua,folder):
		threading.Thread.__init__(self)
		GObject.GObject.__init__(self)		
		self.setDaemon(True)
		self.cua = cua
		self.folder = folder

	def run(self):
		while True:
			fileUrl = self.cua.get()
			if fileUrl is None:
				break
			fileName = name_file(fileUrl)
			basename, extension = os.path.splitext(fileName)
			fileName = os.path.join(self.folder,fileName)
			try:
				print('Downloading %s...'%fileUrl)
				print(fileName)
				output = open(fileName,'wb')
				req = urllib.request.Request(
					fileUrl, 
					data=None, 
					headers={
						'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
					}
				)
				imgData = urllib.request.urlopen(req).read()
				output.write(imgData)
				output.close()
			except:
				print('Not downloaded from %s'%(fileUrl))
			self.emit('downloaded',fileUrl)
			self.cua.task_done()

class Progreso(Gtk.Dialog):
	def __init__(self,title,parent,max_value):
		#
		Gtk.Dialog.__init__(self,title,parent)
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.set_size_request(330, 40)
		self.set_resizable(False)
		self.connect('destroy', self.close)
		#
		vbox1 = Gtk.VBox(spacing = 5)
		vbox1.set_border_width(5)
		self.get_content_area().add(vbox1)
		#
		self.progressbar = Gtk.ProgressBar()
		vbox1.pack_start(self.progressbar,True,True,0)
		#
		self.show_all()
		#
		self.max_value=max_value
		self.value=0.0
		self.map()
		while Gtk.events_pending():
			Gtk.main_iteration()


	def set_value(self,value):
		if value >=0 and value<=self.max_value:
			self.value = value
			fraction=self.value/self.max_value
			self.progressbar.set_fraction(fraction)
			self.map()
			while Gtk.events_pending():
				Gtk.main_iteration()
			if self.value==self.max_value:
				self.hide()		
	def close(self,widget=None):
		self.destroy()

	def increase(self,w,a):
		self.value+=1.0
		fraction=self.value/self.max_value
		self.progressbar.set_fraction(fraction)
		while Gtk.events_pending():
			Gtk.main_iteration()
		if self.value==self.max_value:
			self.hide()

	def decrease(self):
		self.value-=1.0
		fraction=self.value/self.max_value
		self.progressbar.set_fraction(fraction)
		self.map()
		while Gtk.events_pending():
			Gtk.main_iteration()
			
class SL(Gtk.Dialog): # needs GTK, Python, Webkit-GTK
	def __init__(self):
		Gtk.Dialog.__init__(self, 'File Downloader',None,Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.set_size_request(400, 100)
		self.set_title('Ꙩ ubi site file downloader')
		self.connect('destroy', self.close_application)
		#
		vbox0 = Gtk.VBox(spacing = 10)
		vbox0.set_border_width(5)
		self.get_content_area().add(vbox0)
		#
		table1 = Gtk.Table(3,2,False)
		vbox0.add(table1)
		label10 = Gtk.Label('Extension:')
		label10.set_alignment(0, 0.5)
		table1.attach(label10,0,1,0,1)
		#
		self.entry10 = Gtk.Entry()
		table1.attach(self.entry10,1,2,0,1)		
		#
		label11 = Gtk.Label('Url:')
		label11.set_alignment(0, 0.5)
		table1.attach(label11,0,1,1,2)
		#
		self.entry11 = Gtk.Entry()
		table1.attach(self.entry11,1,2,1,2)
		#
		#self.button = Gtk.Button('Select folder')
		#self.button.connect('clicked',self.on_button_clicked)
		#table1.attach(self.button,0,2,2,3)
		#
		self.show_all()
		
	def close_application(self, widget, event, data=None):
		exit(0)

	def on_button_clicked(self,widget):
		dialog =Gtk.FileChooserDialog("Select folder",None,Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_CANCEL, Gtk.ResponseType.REJECT,Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT))
		dialog.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		filter = Gtk.FileFilter()
		filter.set_name("Folder")
		filter.add_pattern("*")  # whats the pattern for a folder
		dialog.add_filter(filter)
		if dialog.run() == Gtk.ResponseType.ACCEPT:
			dialog.hide()
			print(dialog.get_filename())
			self.button.set_label(dialog.get_filename())
		dialog.destroy()
        

def main():
	sl = SL();os.system("mkdir /tmp/site");os.system("echo False > /tmp/site/site-log.txt")
	if sl.run() == Gtk.ResponseType.ACCEPT:
		sl.hide()
		#if sl.button.get_label()!='Select folder':
		folder = '/tmp/site/';
		extension = sl.entry10.get_text()
		url = sl.entry11.get_text()
		if len(url)>0:
			urls = get_file_urls(url,extension)
			total = len(urls)
			if total>0:
				print(urls)
				workers = []
				print(1)
				cua = queue.Queue(maxsize=total+2)
				progreso = Progreso('Downloading from %s'%url,None,total)
				total_workers = total if NUM_THREADS > total else NUM_THREADS
				for i in range(total_workers):
					worker = Worker(cua,folder)
					worker.connect('downloaded',progreso.increase)
					worker.start()
					workers.append(worker)
				print(2)
				for aurl in urls:
					cua.put(aurl)
				# block until all tasks are done
				print(3)
				cua.join()
				# stop workers
				print(4)
				for i in range(total_workers):
					cua.put(None)
				for worker in workers:
					worker.join()
					while Gtk.events_pending():
						Gtk.main_iteration()
						
				os.system("echo True > /tmp/site/site-log.txt")			
if __name__ == '__main__':
    main()
    exit(0)
