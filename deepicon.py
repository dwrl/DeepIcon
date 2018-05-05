#!/usr/bin/python

import os
from os.path import expanduser, isdir, isfile, join
from xdg.BaseDirectory import *
import configparser

from efl.evas import EVAS_ASPECT_CONTROL_VERTICAL
from efl.elementary.icon import Icon, ELM_ICON_LOOKUP_FDO_THEME

_cachedPaths = None
_themes = []
_iconLookup = {}


def _createCachedPaths(*args):
    global _cachedPaths
    global _themes
    try:
        themeName, themeDir = _getIconTheme(args[0])
    except:
        themeName, themeDir = _getIconTheme()

    themeFile = open(os.path.join(themeDir, "index.theme"))
    themeConf = themeFile.read()
    themeFile.close()

    confPars = configparser.RawConfigParser(allow_no_value=True)
    confPars.read_string(themeConf)

    if themeName not in _themes:
        _themes.append(themeName)
    
        path = None
        tmpPaths = []

        for section in confPars.sections():
            for option in confPars[section]:
                if option.lower() == 'size':
                    size = int(confPars[section]['size'])
                    if size not in _cachedPaths:
                        _cachedPaths.update({size: []})
                    if isdir(os.path.join(themeDir, section)):
                        _cachedPaths[size].append(os.path.join(themeDir, section))

    # Test if the theme is inherited and add its parent if necessary
    try:
        parent = confPars['Icon Theme']['Inherits']
        if ',' in parent:
            parentsList = [ x for x in parents.split(',').strip() if x != '']
            for thisParent in parentsList:
                try:
                    _createCachedPaths(thisParent)
                except:
                    pass
        else:
            try:
                _createCachedPaths(parent)
            except:
                pass
    except:
        pass
        



def DeepIcon(parent,name,size):
    global _cachedPaths
    if _cachedPaths == None:
        _cachedPaths = {}
        _createCachedPaths()

    ic = None

    try:
        ic = Icon(parent, standard=name, order_lookup=ELM_ICON_LOOKUP_FDO_THEME, \
                  size_hint_aspect=(EVAS_ASPECT_CONTROL_VERTICAL, 1, 1), \
                  size_hint_min=(size,size))
    except:
        try:
            ic = Icon(parent, standard=_coerceIcon(name,size), order_lookup=ELM_ICON_LOOKUP_FDO_THEME, \
                      size_hint_aspect=(EVAS_ASPECT_CONTROL_VERTICAL, 1, 1), \
                      size_hint_min=(size,size))
        except:
            try:
                ic = Icon(parent, standard='image-missing', order_lookup=ELM_ICON_LOOKUP_FDO_THEME, \
                          size_hint_aspect=(EVAS_ASPECT_CONTROL_VERTICAL, 1, 1), \
                          size_hint_min=(size,size))
            except:
                try:
                    ic = Icon(parent, standard=_coerceIcon('image-missing',size), order_lookup=ELM_ICON_LOOKUP_FDO_THEME, \
                              size_hint_aspect=(EVAS_ASPECT_CONTROL_VERTICAL, 1, 1), \
                              size_hint_min=(size,size))
                except:
                    ic = Icon(parent, standard='close', order_lookup=ELM_ICON_LOOKUP_FDO_THEME, \
                              size_hint_aspect=(EVAS_ASPECT_CONTROL_VERTICAL, 1, 1), \
                              size_hint_min=(size,size))

    return ic



def _coerceIcon(iconName, size):
    themeName, themeDir = _getIconTheme()
    global _iconLookup

    if iconName in _iconLookup:
        if size in _iconLookup[iconName]:
            return _iconLookup[iconName][size]

    names = []
    names.append(iconName)

    #Make sure we get sub- and gnome mime-names just in case
    if '-' in iconName:
        splitName = iconName
        while '-' in splitName:
            splitName = splitName.rsplit('-', 1)[0]
            names.append(splitName)

        #Take care of gnome specifics
        gnomeMimes = []
        for name in names:
            gnomeMimes.append('gnome-mime-' + name)
        if gnomeMimes != []:
            names.extend(gnomeMimes)

    # Try to get icon from theme
    for name in names:
        iconPath = _getIconPath(themeDir,iconName,name,size)
        if iconPath != None:
            break

    # Else try it from 'hicolor' theme
    if iconPath == None:
        themeName, themeDir = _getIconTheme('hicolor')
        for name in names:
            iconPath = _getIconPath(themeDir,iconName,name,size)
            if iconPath != None:
                break
    return iconPath


def _getIconTheme(*args):
    themeName = None
    if args:
        if len(args) == 1:
            themeName = args[0]
    if themeName == None:
        try:
            themeName = os.environ["E_ICON_THEME"]
        except:
            pass
            #TODO: Add some gconf, dconf, lxde and or kde tests too

    #If not suplied, or in env try to get anything
    if themeName == None or themeName == '' or themeName == False:
        if isdir('/usr/share/icons/gnome'):
            themeName = 'gnome'
        if isdir('/usr/share/icons/breath'):
            themeName = 'gnome'
        if isdir('/usr/share/icons/oxygen'):
            themeName = 'gnome'
        elif isdir('/usr/share/icons/hicolor'):
            themeName = 'hicolor'
        elif isdir('/usr/share/icons/default'):
            themeName = 'default'

    #Now get the theme directory
    if isdir(os.path.join(os.path.expanduser("~"), '.icons', themeName)) \
             and isfile(os.path.join(os.path.expanduser("~"), '.icons', themeName, 'index.theme')):
        themeDir = os.path.join(os.path.expanduser("~"), '.icons', themeName)
    elif isdir(os.path.join('/usr/share/icons', themeName)) \
               and isfile(os.path.join('/usr/share/icons', themeName, 'index.theme')):
        themeDir = os.path.join('/usr/share/icons', themeName)

    return themeName, themeDir



def _getIconPath(themeDir,baseName,name,size):
    global _cachedPaths
    global _iconLookup

    iconPath = None

    #Look if the size already is right:
    if size in _cachedPaths.keys():
        for path in _cachedPaths[size]:
            if isfile(os.path.join(path, name + '.png')):
                iconPath =  os.path.join(path, name + '.png')
            elif isfile(os.path.join(path, name + '.svg')):
                iconPath =  os.path.join(path, name + '.svg')

    if iconPath == None:
        #Try to get next biggest size
        for tmpSize in sorted([x for x in _cachedPaths.keys() if x > size]):
            for path in _cachedPaths[tmpSize]:
                if isfile(os.path.join(path, name + '.png')):
                    iconPath =  os.path.join(path, name + '.png')
                    break
                elif isfile(os.path.join(path, name + '.svg')):
                    iconPath =  os.path.join(path, name + '.svg')
                    break

    if iconPath == None:
        #Try to get next smallest size
        for tmpSize in sorted([x for x in _cachedPaths.keys() if x < size]):
            for path in _cachedPaths[tmpSize]:
                if isfile(os.path.join(path, name + '.png')):
                    iconPath =  os.path.join(path, name + '.png')
                    break
                elif isfile(os.path.join(path, name + '.svg')):
                    iconPath =  os.path.join(path, name + '.svg')
                    break

    if iconPath != None:
        if baseName not in _iconLookup:
            _iconLookup.update({baseName: {}})
        if size not in _iconLookup[baseName]:
            _iconLookup[baseName].update({size: iconPath})

    return iconPath
