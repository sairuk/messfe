#!/usr/bin/env python

import os, sys, glob
import xml.etree.ElementTree as etree
import subprocess
from subprocess import Popen

import pygtk
pygtk.require('2.0')
import gtk

notfound = 'default.png'
w, h = 1280, 800

profile = {
  'name':'MESS',
  'bios_path':'/mnt/ext4/library/roms/Bios/MESS - ROMs',
  'rom_path':'/mnt/ext4/library/roms/Bios/Mess Software Lists',
  'art_path':'/mnt/ext4/library/roms/Artwork/Bios/MESS',
  'executable':'/usr/games/mess',
  'info_file':'messinfo.xml',
  'info_gen':'-lx',
  'elem_tag':'machine',
  'columns_sys':['System','rom','device'],
  'columns_soft':['Software','rom','path']
}

class UI():
  def destroy(self, widget):
    """ destroy window """
    gtk.main_quit()
    
  def __init__(self):
    window = gtk.Window()
    window.connect("destroy", self.destroy)
    window.set_title(profile['name'])
    window.set_border_width(0)
    window.set_size_request(w, h)
    hbox = gtk.HBox(True, 0)
    hbox.set_size_request(int(w*0.7), h) 
    self.w, self.h = hbox.get_size_request()
    vbox = gtk.HPaned()
    self.rom_name = ""

    ### Systems List
    scrolled_window = gtk.ScrolledWindow()
    scrolled_window.set_size_request(int(self.w*0.2), h) 
    scrolled_window.set_border_width(10)
    scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
    # Build Treeview LS & TV done here to target events
    self.listmodel_sys = gtk.ListStore(str, str, str)
    self.sys_view = gtk.TreeView(model=self.listmodel_sys)
    scrolled_window.add(self.build_list(self.listmodel_sys, read_sys(), profile['columns_sys'],self.sys_view))
    # Add Events
    self.sys_view.get_selection().connect('changed',self.sys_on_changed)
    # Attach to Window
    hbox.pack_start(scrolled_window, True, True, 0)    
    window.add(vbox)
    # Set default selection
    pass
        
    ### Roms List
    scrolled_window_soft = gtk.ScrolledWindow()
    scrolled_window_soft.set_size_request(int(self.w*0.8), h) 
    scrolled_window_soft.set_border_width(10)
    scrolled_window_soft.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
    # Build Treeview
    self.listmodel_soft = gtk.ListStore(str, str, str)
    self.soft_view = gtk.TreeView(model=self.listmodel_soft)
    self.items_soft = [["","",""]]
    scrolled_window_soft.add(self.build_list(self.listmodel_soft, self.items_soft, profile['columns_soft'],self.soft_view))
    # Add events
    self.soft_view.get_selection().connect('changed',self.soft_on_changed)
    self.soft_view.add_events(gtk.gdk.BUTTON_PRESS_MASK )
    self.soft_view.connect('button_press_event', self.selectTest)
    # Attach to Window
    hbox.pack_start(scrolled_window_soft, True, True, 1)
    vbox.pack1(hbox, True, False)


    
    ### Screenshot Bit
    sbox = gtk.VBox(True, 0)
    sbox.set_size_request(int(w*0.3), h)
    self.ingame = gtk.Image()
    self.ingame.set_from_file(notfound)
    sbox.pack_start(self.ingame, True, True, 0)
    self.title = gtk.Image()
    self.title.set_from_file(notfound)
    sbox.pack_end(self.title, True, True, 0)
    self.cover = gtk.Image()
    self.cover.set_from_file(notfound)
    sbox.pack_end(self.cover, True, True, 0)

    vbox.pack2(sbox, True, True)

    window.show_all()
    return

  def build_list(self, listmodel, item, columns, view, coldraw=True):
    """ build treeview lists """
    listmodel.clear()
    for i in range(len(item)):
      listmodel.append(item[i])
    if coldraw:
      for i in range(len(columns)):
        cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn(columns[i], cell, text=i)
        view.append_column(col)
    view.queue_draw()
    return view

  def run_system(self):
    """ exec system with args """
    path_check()
    p = Popen([profile['executable'],self.sys_name, "-"+self.sys_device, self.soft_path])
    
  def redraw_list(self, system):
    """ redraw software lists for system """
    self.build_list(self.listmodel_soft, read_soft(system), profile['columns_soft'],self.soft_view, False)
    
  def redraw_image(self, system, soft):
    """ update images """
    self.ingame.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(notfound))
    self.title.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(notfound))
    self.cover.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(notfound))
    if os.path.exists(profile['art_path']) and soft:
      basepath = os.path.join(profile['art_path'],system)
      basefile = soft+'.png'
      ingame = os.path.join(basepath,'ingame',basefile)
      title = os.path.join(basepath,'titles',basefile)
      cover = os.path.join(basepath,'cover',basefile)
      if os.path.exists(ingame):
        self.ingame.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(ingame))
        self.ingame.queue_draw()
      if os.path.exists(title):
        self.title.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(title))
        self.title.queue_draw()
      if os.path.exists(cover):
        self.cover.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(cover))
        self.cover.queue_draw()
    return

  def selectTest(self, widget, event):
    """ double click event, run system """
    if event.button == 1 and event.type == gtk.gdk._2BUTTON_PRESS:
      self.run_system()
    return

  def soft_on_changed(self, selection):
    """ software treeview on change event """
    (model, pathlist) = selection.get_selected_rows()
    for path in pathlist :
      tree_iter = model.get_iter(path)
      self.soft_desc = model.get_value(tree_iter,0)
      self.soft_name = model.get_value(tree_iter,1)
      self.soft_path = model.get_value(tree_iter,2)
    return self.redraw_image(self.sys_name, self.soft_name)

  def sys_on_changed(self, selection):
    """ system treeview on change event """
    (model, pathlist) = selection.get_selected_rows()
    for path in pathlist :
      tree_iter = model.get_iter(path)
      self.sys_desc = model.get_value(tree_iter,0)
      self.sys_name = model.get_value(tree_iter,1)
      self.sys_device = model.get_value(tree_iter,2)
    return self.redraw_list(self.sys_name)

def write_log(msg, flush=False, stdout=True):
	"""	write to screen	"""
	if stdout:
		if flush:
			sys.stdout.write("\r%s" % msg)
			sys.stdout.flush()
		else:
			sys.stdout.write("%s" % msg)			
	return

def read_soft(system):
  """ read available software """
  if os.path.exists(profile['rom_path']):
    rom_path = [x for x in glob.glob(os.path.join(profile['rom_path'],system,'*'))]
    rp = []
    for r in rom_path:
      rp.append([os.path.basename(r).split('.')[0],os.path.basename(r).split('.')[0],r])
    return rp
  else:
    return ["","",""]
  return

def read_sys():  
  """ read available system """
  print "Parsing XML ... Please Wait"
  xmL = profile['info_file']

  if not os.path.exists(xmL):
    return
  
  # Build RomPath List (only filename)
  if os.path.exists(profile['bios_path']):
    rom_path = [os.path.basename(x).split('.')[0] for x in glob.glob(os.path.join(profile['bios_path'],'*'))]
  else:
    return

  rom_desc = ""
  have_rom = False
  good_sys = True
  msg = 0
  old_msg = 0
  games = []
  
  for event, elem in etree.iterparse(xmL, events=('start', 'end', 'start-ns', 'end-ns')):
    if event == 'start' and elem.tag == profile['elem_tag']:
      within_ns = True
      ### Game Start
      rom_attr = elem.attrib['name'] 
      if rom_attr in rom_path:
        have_rom = True
      else:
        have_rom = False
        
    elif elem.tag == "description" and within_ns:
      ### Game Description
      rom_desc = elem.text
        
    elif elem.tag == "driver" and within_ns:
      ### Emulation Status
      if elem.attrib['status'] == "imperfect":
        good_sys = False
      else:
        good_sys = True
        
    elif elem.tag == "device" and within_ns:
      #Device attached to system
      device_type = elem.attrib['type']
      for dev in elem:
        if dev.tag == "instance":
          device_type = dev.attrib['briefname']
        break

    if event == 'end' and elem.tag == profile['elem_tag']:
      within_ns = False

    if have_rom and good_sys and not within_ns:
      games.append([rom_desc, rom_attr, device_type])
      have_rom = False
      good_sys = False 
            
  print "Parsing XML ... Complete, loading UI"
  return games

def check_profile(path):
    """ check required paths exist """
    if path and not os.path.exists(path):
      print "ERROR: %s does not exist, exiting" % path
      sys.exit()
    return
    
def path_check():
  """ check required paths exist """
  path_list = [profile['bios_path'], profile['rom_path'], profile['executable']]
  for p in path_list:
    check_profile(p) 
  
if __name__ == '__main__':
  # Generate File
  if not os.path.exists(profile['info_file']):
    print "Generating File %s" % profile['info_file']
    s = Popen([profile['executable'], profile['info_gen']],
    shell=False,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT)
    output = s.communicate()[0]
    # Write output
    f = open(profile['info_file'],'w')
    f.write(output)
    f.close()
  # Launch UI
  path_check()
  UI()
  gtk.main()
