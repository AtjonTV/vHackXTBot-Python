#!/usr/bin/python2.7
# -*- coding: utf-8

from utils import Utils

import json
import logging
import random
logger = logging.getLogger(__name__)


class Botnet:
    ut = Utils()

    def __init__(self, player):
        self.username = player.username
        self.password = player.password
        self.uhash = player.uhash
        self.botNetServers = 3
        self.botnet = []
        self.p = player
        self.ofwhat = ["fw", "av", "smash", "mwk"]
        self._initbot()

    def _initbot(self):
        """
        Grab the amount of bots in the botnet
        and populate and array of Bot class
        :return: none
        """
        data = self._botnetInfo()
        bots = json.loads(data)
        self.botnet = []
        if int(bots['count']) > 0:
            for i in bots['data']:
                self.energy = bots['energy']
                if self.energy > 0:
                    bot = Bot(i['running'], self.ofwhat[random.randint(0,3)], self.energy, self.username, self.password, self.uhash)
                    self.botnet.append(bot)

    def printbots(self):
        """
        Print a list of player PCs in the botnet
        :return: None
        """
        for bot in self.botnet:
            logger.info(bot)

    def getbotnetdata(self):
        """
        Return an array of bot class.
        Contains all the bots in the botnet.
        :return: list of bot class
        """
        return self.botnet

    def getInfo(self):
        """
        Get info about the entire botnet.
        Including if you can attack bot net servers etc.
        Also botnet PC info.
        :return: list of vHack serves that can be hacked.
                 ['1','2','1']. '1' = can be hacked, '2' time not elapsed.
        """
        response = self.ut.requestString(self.username, self.password, self.uhash, "vh_botnetInfo.php")
        response = json.loads(response)
        return response

    def attack(self):
        """
        Check if vHack server botnet is attackable,
        then attack if can.
        :return: none
        """
        self._initbot()
        logger.info("Trying Bot Net")
        cinfo = self.getInfo()

        for i in range(1, self.botNetServers + 1):
            if cinfo[i - 1] == '1':
                logger.debug('attacking #{}'.format(i))
                if i == 1:
                    response = self.ut.requestString(self.username, self.password, self.uhash, "vh_attackCompany.php", company=str(i))
                else:
                    response = self.ut.requestString(self.username, self.password, self.uhash, "vh_attackCompany" + str(i) + ".php", company=str(i))
                logger.debug('attack #{} response {}'.format(i, response))
                if response == '0':
                    logger.info('#{} Netcoins gained'.format(i))
                else:
                    logger.info('#{} Failed! No netcoins...'.format(i))
            else:
                logger.info("Botnet #{} not hackable as yet".format(i))

    def upgradebotnet(self, hostname, running):
        """
        Check if there is enough money to upgrade a botnet PC.
        Cycle through and upgrade until no money.
        :return: None
        """
        ofwhat = self.ofwhat[random.randint(0,3)]
        logger.info("Attempting to upgrade bot net PC's "+ hostname + " [" + ofwhat + "]")
        for i in self.botnet:
            while (int(self.p.getmoney()) > int(i.nextlevelcostenergy()) and i.botupgradable()):
                new_bal = i.upgradesinglebot(hostname, ofwhat, running)
                if new_bal is not None and new_bal == True:
                    logger.info("wait botnet update working for " + hostname + "...")
                    self.p.setmoney(new_bal)
                else:
                    logger.info("your are not energy for update " + hostname + " :(")
                    break
            logger.debug("#{} not upgradeable".format(hostname))

    def _botnetInfo(self):
        """
        Get the botnet information including vHack servers and PC data.
        :return: string
        '{"count":"14",
        "data":[{"bID":"1","bLVL":"100","bSTR":"100","bPRICE":"10000000"},
        {"bID":"2","bLVL":"100","bSTR":"100","bPRICE":"10000000"}],
        "strength":23,"resethours1":"","resetminutes1":"14","resethours2":"4","resetminutes2":"15",
        "resethours3":"3","resetminutes3":"15",
        "canAtt1":"2","canAtt2":"2","canAtt3":"2"}'
        """
        temp = self.ut.requestString(self.username, self.password, self.uhash, "vh_botnetInfo.php")
        return temp

    def __repr__(self):
        return "Botnet details: vHackServers: {0}, Bot Net PC's: {1}".format(self.botNetServers, self.botnet)


class Bot:
    ut = Utils()

    def __init__(self, running, ofwhat, energy, username, password, uhash):
        self.username = username
        self.uhash = uhash
        self.password = password
        self.running = int(running)
        self.ofwhat = ofwhat
        self.energy = energy

    def botupgradable(self):
        """
        Determine if botnet PC is at max level or not.
        :return: Bool
        """
        if self.running == 0:
            return True
        else:
            return False

    def nextlevelcostenergy(self):
        """
        Return the cost of upgrading bot to the next level
        :return:int
        """
        return self.energy

    def parse_json_stream(self, stream):
        decoder = json.JSONDecoder()
        while stream:
            obj, idx = decoder.raw_decode(stream)
            yield obj
            stream = stream[idx:].lstrip()

    def upgradesinglebot(self, hostname, ofwhat, running):
        """
        Pass in bot class object and call upgrade function based on bot ID.
        details :
        {u'strength': u'22', u'old': u'30', u'mm': u'68359859',
        u'money': u'66259859', u'costs': u'2100000',
        u'lvl': u'21', u'new': u'22'}
        current lvl, bot number, x, x, upgrade cost, lvl, next lvl
        :return: None
        """
        if running == 0:
            response = self.ut.requestString(self.username, self.password, self.uhash, "vh_upgradePC.php", hostname=hostname, ofwhat=ofwhat)
            # not loads the json bug python... try to resolve
            return True
        else:
            return False

    def __repr__(self):
        return "Bot details: id: {0}, Level: {1}, Next Cost: {2}".format(self.id, self.lvl, self.upgradecost)
