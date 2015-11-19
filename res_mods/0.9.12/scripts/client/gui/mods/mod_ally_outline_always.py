# Embedded file name: mod_ally_outline_always
"""for 0.9.10 fixed by webium, all credits goes to locastan"""
import BigWorld, Keys
from gui.app_loader import g_appLoader
import Vehicle
from Vehicle import Vehicle
import xml.dom.minidom
import ResMgr
import os
import Math
import json
import game
from AvatarInputHandler.control_modes import SniperControlMode
from debug_utils import *
from gui.Scaleform.Battle import Battle

class Silouhette:
    __currTime = None
    __enableRenderModel = True

    def ally_silouhette(self):
        if self.__enableRenderModel:
            try:
                BigWorld.wgSetEdgeDetectColors((self.__color, self.__enemyhigh, self.__allyhigh))
                player = BigWorld.player()
                if player is not None:
                    if hasattr(player, 'isOnArena'):
                        curCtrl = getattr(getattr(BigWorld.player(), 'inputHandler', None), 'ctrl', None)
                        if player.isOnArena:
                            for v in BigWorld.entities.values():
                                if isinstance(v, Vehicle):
                                    if v.isAlive() and v.isStarted:
                                        if v.publicInfo['team'] is BigWorld.player().team:
                                            target = BigWorld.target()
                                            if BigWorld.entity(BigWorld.player().playerVehicleID) is not None and BigWorld.entity(v.id) is not None:
                                                distance = (BigWorld.entity(BigWorld.player().playerVehicleID).position - BigWorld.entity(v.id).position).length
                                            else:
                                                distance = 1
                                            if target is not None and target.id == v.id:
                                                BigWorld.wgDelEdgeDetectEntity(v)
                                                BigWorld.wgAddEdgeDetectEntity(v, 2, False)
                                            elif int(v.id) != int(BigWorld.player().playerVehicleID) and distance <= self.__distancevalue or self.__sniperonly == True and not isinstance(curCtrl, SniperControlMode):
                                                BigWorld.wgDelEdgeDetectEntity(v)
                                            elif int(v.id) == int(BigWorld.player().playerVehicleID):
                                                continue
                                            else:
                                                BigWorld.wgDelEdgeDetectEntity(v)
                                                BigWorld.wgAddEdgeDetectEntity(v, 0, False)
                                    else:
                                        BigWorld.wgDelEdgeDetectEntity(v)

            except TypeError as err:
                print ('[ally_silouhette] Error: ', err)

        return

    def keypressed(self):
        if self.__enableRenderModel:
            if g_appLoader.getDefBattleApp() is not None:
                g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'Ally Outlines  OFF', 'gold'])
                self.__enableRenderModel = False
                for v in BigWorld.entities.values():
                    if type(v) is Vehicle:
                        BigWorld.wgDelEdgeDetectEntity(v)

        elif g_appLoader.getDefBattleApp() is not None:
            self.__enableRenderModel = True
            g_appLoader.getDefBattleApp().call('battle.PlayerMessagesPanel.ShowMessage', ['0', 'Ally Outlines  ON', 'gold'])
            BigWorld.Silouhette.ally_silouhette()
        return

    def parsePaths(self):
        global silouhetteConfigFile
        try:
            wd = None
            sec = ResMgr.openSection('../paths.xml')
            subsec = sec['Paths']
            vals = subsec.values()
            for val in vals:
                path = val.asString + '/../'
                if os.path.isdir(path) and os.path.isfile(path + '/configs/silouhette.xml'):
                    wd = path
                    break

            if not wd:
                raise Exception('UT_announcer.xml is not found in the paths')
        except Exception as err:
            print ('[ally_silouhette] Error locating working directory: ', err)
            wd = 'res_mods/%s/%s' % (ver, os.path.dirname(__file__))
            print '[ally_silouhette]   fallback to the default path: %s' % wd

        silouhetteConfigFile = wd + '/configs/silouhette.xml'
        try:
            xmlfile = xml.dom.minidom.parse(silouhetteConfigFile)
            self.__distancevalue = int(xmlfile.getElementsByTagName('distance')[0].childNodes[0].nodeValue)
            self.__sniperonly = True if xmlfile.getElementsByTagName('sniperonly')[0].childNodes[0].nodeValue == 'true' else False
            togglekey = xmlfile.getElementsByTagName('togglekey')[0].childNodes[0].nodeValue
            self.__color = Math.Vector4(json.loads(xmlfile.getElementsByTagName('color')[0].childNodes[0].nodeValue))
            self.__enemyhigh = Math.Vector4(json.loads(xmlfile.getElementsByTagName('enemyhighlight')[0].childNodes[0].nodeValue))
            self.__allyhigh = Math.Vector4(json.loads(xmlfile.getElementsByTagName('allyhighlight')[0].childNodes[0].nodeValue))
        except Exception as err:
            print '[AllyOutlines] exception', err
            self.__distancevalue = 100
            togglekey = 'KEY_NUMPAD1'
            self.__sniperonly = False
            self.__color = Math.Vector4(0.2, 0.2, 0.2, 0.5)
            self.__enemyhigh = Math.Vector4(1, 0, 0, 0.5)
            self.__allyhigh = Math.Vector4(0, 1, 0, 0.5)

        self.__KEY_RENDER_MODEL = getattr(Keys, togglekey)
        return

    def silhkKeyEvent(self, isDown, key, mods):
        try:
            if hasattr(BigWorld.player(), 'arena') and hasattr(BigWorld, 'Silouhette'):
                BPA = BigWorld.player().arena
                if isDown:
                    if BigWorld.isKeyDown(BigWorld.Silouhette.__KEY_RENDER_MODEL):
                        BigWorld.Silouhette.keypressed()
                    BigWorld.Silouhette.ally_silouhette()
        except Exception as e:
            print ('Allied Silouhette error: ', str(e))
        finally:
            return BigWorld.Silouhette.oldHKey(isDown, key, mods)


BigWorld.Silouhette = Silouhette()

def _stopVisual(current, old_stopVisual = Vehicle.stopVisual):
    old_stopVisual(current)
    BigWorld.wgDelEdgeDetectEntity(current)


Vehicle.stopVisual = _stopVisual
from Avatar import PlayerAvatar

def _targetFocus(current, entity, old_targetFocus = PlayerAvatar.targetFocus):
    BigWorld.wgDelEdgeDetectEntity(entity)
    old_targetFocus(current, entity)


PlayerAvatar.targetFocus = _targetFocus
org_afterCreate = Battle.afterCreate

def new_silafterCreate(self):
    org_afterCreate(self)
    BigWorld.Silouhette.parsePaths()
    #BigWorld.player().inputHandler.onCameraChanged += BigWorld.Silouhette.ally_silouhette()
    BigWorld.Silouhette.oldHKey = BigWorld.player().handleKey
    BigWorld.player().handleKey = BigWorld.Silouhette.silhkKeyEvent


Battle.afterCreate = new_silafterCreate
org_beforeDelete = Battle.beforeDelete

def new_silbeforeDelete(self):
    BigWorld.player().handleKey = BigWorld.Silouhette.oldHKey
    org_beforeDelete(self)


Battle.beforeDelete = new_silbeforeDelete
