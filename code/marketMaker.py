from BSE import Trader, Order
from BSE import Trader_Giveaway, Trader_ZIC, Trader_Shaver, Trader_Sniper, Trader_ZIP
from numpy.random import normal #from random import gauss
from numpy import argmax
# import pdb

class Trader_MAB( Trader ):


  def __init__(self, ttype, tid, balance):
    # Predefine initial parameters
    self.earn = 0
    self.uncertainty = 10
    # ############################

    self.ttype = ttype
    self.tid = tid
    self.balance = balance
    self.blotter = []
    self.orders = []
    self.willing = 1        #?
    self.able = 1           #?
    self.lastquote = None   #?

    # predefined for this system: GVWY, ZIC, SHVR, SNPR, ZIP, MAB
    ## Initialise all available traders: GVWY, ZIC, SHVR, SNPR, ZIP, MAB
    # self.traders = [ 'GVWY', 'ZIC', 'SHVR', 'SNPR', 'ZIP' ]
    # self.MAB_GVWY = Trader_Giveaway('GVWY', tid, balance)
    # self.MAB_ZIC = Trader_ZIC('ZIC', tid, balance)
    # self.MAB_SHVR = Trader_Shaver('SHVR', tid, balance)
    # self.MAB_SNPR = Trader_Sniper('SNPR', tid, balance)
    # self.MAB_ZIP = Trader_ZIP('ZIP', tid, balance)
    self.keys = [ 'GVWY', 'ZIC', 'SHVR', 'SNPR', 'ZIP' ]
    self.traders = { 'GVWY' : Trader_Giveaway('GVWY', tid, balance),
      'ZIC' : Trader_ZIC('ZIC', tid, balance),
      'SHVR' : Trader_Shaver('SHVR', tid, balance),
      'SNPR' : Trader_Sniper('SNPR', tid, balance),
      'ZIP' : Trader_ZIP('ZIP', tid, balance) }

    ## Get all available traders count
    self.tradersNo = len(self.traders)

    # Initialise 'trade-ness' parameters
    self.mu = dict( zip(keys, self.tradersNo * [self.earn]) )
    self.sigma = dict( zip(keys, self.tradersNo * [self.uncertainty]) )
    # self.mu = self.tradersNo * [self.earn]
    # self.sigma = self.tradersNo * [self.uncertainty]


    def add_order(self, order):
      # in this version, trader has at most one order,
      # if allow more than one, this needs to be self.orders.append(order)
      self.orders=[order]
      # Remember about sub-traders
      for traderID in self.traders:
        self.traders[traderID].add_order(order)
      # self.MAB_GVWY.add_order(order)
      # self.MAB_ZIC.add_order(order)
      # self.MAB_SHVR.add_order(order)
      # self.MAB_SNPR.add_order(order)
      # self.MAB_ZIP.add_order(order)


    def del_order(self, order):
      # this is lazy: assumes each trader has only one order with quantity=1, so deleting sole order
      # CHANGE TO DELETE THE HEAD OF THE LIST AND KEEP THE TAIL
      self.orders = []
      # Remember about sub-traders
      for traderID in self.traders:
        self.traders[traderID].del_order(order)
      # self.MAB_GVWY.del_order(order)
      # self.MAB_ZIC.del_order(order)
      # self.MAB_SHVR.del_order(order)
      # self.MAB_SNPR.del_order(order)
      # self.MAB_ZIP.del_order(order)

    def bookkeep(self, trade, order, verbose):
      outstr='%s (%s) bookkeeping: orders=' % (self.tid, self.ttype)
      for order in self.orders: outstr = outstr + str(order)

      self.blotter.append(trade) # add trade record to trader's blotter
      # NB What follows is **LAZY** -- assumes all orders are quantity=1
      transactionprice = trade['price']
      if self.orders[0].otype == 'Bid':
        profit = self.orders[0].price-transactionprice
      else:
        profit = transactionprice-self.orders[0].price
      self.balance += profit
      if verbose: print('%s profit=%d balance=%d ' % (outstr, profit, self.balance))
      self.del_order(order) # delete the order
      # Remember about sub-traders
      for traderID in self.traders:
        self.traders[traderID].bookkeep(trade, order, verbose)
      # self.MAB_GVWY.bookkeep(trade, order, verbose)
      # self.MAB_ZIC.bookkeep(trade, order, verbose)
      # self.MAB_SHVR.bookkeep(trade, order, verbose)
      # self.MAB_SNPR.bookkeep(trade, order, verbose)
      # self.MAB_ZIP.bookkeep(trade, order, verbose)


  # Get order, calculate trading price, and schedule
  def getorder( self, time, countdown, lob ):

    # Get order from selected trader
    def simulateTraders( TCL, traderID ):
      return self.traders[traderID].getorder( *TCL )
      # self.MAB_GVWY.getorder( *TCL )
      # self.MAB_ZIC.getorder( *TCL )
      # self.MAB_SHVR.getorder( *TCL )
      # self.MAB_SNPR.getorder( *TCL )
      # self.MAB_ZIP.getorder( *TCL )

    if len( self.orders ) < 1:
      order = None
    else:
      ## Get samples
      action = normal(self.mu.values(), self.sigma.values())
      ## Choose algorithm
      choice = argmax(action)
      ## Identify trader associated with choice
      traderID = self.keys[choice]
      ## Simulate chosen trader
      order = simulateTrader((time, countdown, lob), traderID)

      ## Get order details
      # price = self.orders[0].price
      # orderType = self.orders[0].otype
      # quantity = self.orders[0].qty
      # (GVWYo,ZICo,SHVRo,SNPRo,ZIPo) = simulateTrader((time, countdown, lob), traderID)
      # order = Order( self.tid, orderType, price, quantity, time )

    return order


  # Update trader's statistics based on current market situation
  def respond(self, time, lob, trade, verbose):

    ## Analyse and produce the response
    #...
    print "Time: ", time, " lob: ", lob
    #pdb.set_trace()


#                 else:
#                         self.active = True
#                         self.limit = self.orders[0].price
#                         self.job = self.orders[0].otype
#                         if self.job == 'Bid':
#                                 # currently a buyer (working a bid order)
#                                 self.margin = self.margin_buy
#                         else:
#                                 # currently a seller (working a sell order)
#                                 self.margin = self.margin_sell
#                         quoteprice = int(self.limit * (1 + self.margin))
#                         self.price = quoteprice

#                         order=Order(self.tid, self.job, quoteprice, self.orders[0].qty, time)

#                 return order


#         # update margin on basis of what happened in market
#         def respond( lob, trade):
#                 # ZIP trader responds to market events, altering its margin
#                 # does this whether it currently has an order to work or not

#                 def target_up(price):
#                         # generate a higher target price by randomly perturbing given price
#                         ptrb_abs = self.ca * random.random() # absolute shift
#                         ptrb_rel = price * (1.0 + (self.cr * random.random()) ) # relative shift
#                         target=int(round(ptrb_rel + ptrb_abs,0))
# ##                        print('TargetUp: %d %d\n' % (price,target))
#                         return(target)


#                 def target_down(price):
#                         # generate a lower target price by randomly perturbing given price
#                         ptrb_abs = self.ca * random.random() # absolute shift
#                         ptrb_rel = price * (1.0 - (self.cr * random.random()) ) # relative shift
#                         target=int(round(ptrb_rel - ptrb_abs,0))
# ##                        print('TargetDn: %d %d\n' % (price,target))
#                         return(target)


#                 def willing_to_trade(price):
#                         # am I willing to trade at this price?
#                         willing = False
#                         if self.job == 'Bid' and self.active and self.price >= price:
#                                 willing = True
#                         if self.job == 'Ask' and self.active and self.price <= price:
#                                 willing = True
#                         return willing


#                 def profit_alter(price):
#                         oldprice = self.price
#                         diff = price - oldprice
#                         change = ((1.0-self.momntm)*(self.beta*diff)) + (self.momntm*self.prev_change)
#                         self.prev_change = change
#                         newmargin = ((self.price + change)/self.limit) - 1.0

#                         if self.job=='Bid':
#                                 if newmargin < 0.0 :
#                                         self.margin_buy = newmargin
#                                         self.margin = newmargin
#                         else :
#                                 if newmargin > 0.0 :
#                                         self.margin_sell = newmargin
#                                         self.margin = newmargin

#                         #set the price from limit and profit-margin
#                         self.price = int(round(self.limit*(1.0+self.margin),0))
# ##                        print('old=%d diff=%d change=%d price = %d\n' % (oldprice, diff, change, self.price))


#                 # what, if anything, has happened on the bid LOB?
#                 bid_improved = False
#                 bid_hit = False
#                 lob_best_bid_p = lob['bids']['best']
#                 lob_best_bid_q = None
#                 if lob_best_bid_p != None:
#                         # non-empty bid LOB
#                         lob_best_bid_q = lob['bids']['lob'][-1][1]
#                         if self.prev_best_bid_p < lob_best_bid_p :
#                                 # best bid has improved
#                                 # NB doesn't check if the improvement was by self
#                                 bid_improved = True
#                         elif trade != None and ((self.prev_best_bid_p > lob_best_bid_p) or ((self.prev_best_bid_p == lob_best_bid_p) and (self.prev_best_bid_q > lob_best_bid_q))):
#                                 # previous best bid was hit
#                                 bid_hit = True
#                 elif self.prev_best_bid_p != None:
#                         # the bid LOB has been emptied by a hit
#                                 bid_hit = True

#                 # what, if anything, has happened on the ask LOB?
#                 ask_improved = False
#                 ask_lifted = False
#                 lob_best_ask_p = lob['asks']['best']
#                 lob_best_ask_q = None
#                 if lob_best_ask_p != None:
#                         # non-empty ask LOB
#                         lob_best_ask_q = lob['asks']['lob'][0][1]
#                         if self.prev_best_ask_p > lob_best_ask_p :
#                                 # best ask has improved -- NB doesn't check if the improvement was by self
#                                 ask_improved = True
#                         elif trade != None and ((self.prev_best_ask_p < lob_best_ask_p) or ((self.prev_best_ask_p == lob_best_ask_p) and (self.prev_best_ask_q > lob_best_ask_q))):
#                                 # trade happened and best ask price has got worse, or stayed same but quantity reduced -- assume previous best ask was lifted
#                                 ask_lifted = True
#                 elif self.prev_best_ask_p != None:
#                         # the bid LOB is empty now but was not previously, so must have been hit
#                                 ask_hit = True


#                 if verbose and (bid_improved or bid_hit or ask_improved or ask_lifted):
#                         print ('B_improved',bid_improved,'B_hit',bid_hit,'A_improved',ask_improved,'A_lifted',ask_lifted)


#                 deal =  bid_hit or ask_lifted

#                 if self.job == 'Ask':
#                         # seller
#                         if deal :
#                                 tradeprice = trade['price']
#                                 if self.price <= tradeprice:
#                                         # could sell for more? raise margin
#                                         target_price=target_up(tradeprice)
#                                         profit_alter(target_price)
#                                 elif ask_lifted and self.active and not willing_to_trade(tradeprice):
#                                         # wouldnt have got this deal, still working order, so reduce margin
#                                         target_price=target_down(tradeprice)
#                                         profit_alter(target_price)
#                         else:
#                                 # no deal: aim for a target price higher than best bid
#                                 if ask_improved and self.price > lob_best_ask_p:
#                                         if lob_best_bid_p != None:
#                                                 target_price = target_up(lob_best_bid_p)
#                                         else:
#                                                 target_price = lob['asks']['worst'] # stub quote
#                                         profit_alter(target_price)

#                 if self.job == 'Bid':
#                         # buyer
#                         if deal :
#                                 tradeprice = trade['price']
#                                 if self.price >= tradeprice:
#                                         # could buy for less? raise margin (i.e. cut the price)
#                                         target_price=target_down(tradeprice)
#                                         profit_alter(target_price)
#                                 elif bid_hit and self.active and not willing_to_trade(tradeprice):
#                                         # wouldnt have got this deal, still working order, so reduce margin
#                                         target_price=target_up(tradeprice)
#                                         profit_alter(target_price)
#                         else:
#                                 # no deal: aim for target price lower than best ask
#                                 if bid_improved and self.price < lob_best_bid_p:
#                                         if lob_best_ask_p != None:
#                                                 target_price = target_down(lob_best_ask_p)
#                                         else:
#                                                 target_price = lob['bids']['worst'] # stub quote
#                                         profit_alter(target_price)


#                 # remember the best LOB data ready for next response
#                 self.prev_best_bid_p = lob_best_bid_p
#                 self.prev_best_bid_q = lob_best_bid_q
#                 self.prev_best_ask_p = lob_best_ask_p
#                 self.prev_best_ask_q = lob_best_ask_q
