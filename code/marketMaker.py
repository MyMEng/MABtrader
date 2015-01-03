from BSE import Trader, Order
from BSE import Trader_Giveaway, Trader_ZIC, Trader_Shaver, Trader_Sniper, Trader_ZIP
import random

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
    self.traders = [ 'GVWY', 'ZIC', 'SHVR', 'SNPR', 'ZIP' ]
    self.MAB_GVWY = Trader_Giveaway('GVWY', 'MAB_GVWY', 0.00)
    self.MAB_ZIC = Trader_ZIC('ZIC', 'MAB_ZIC', 0.00)
    self.MAB_SHVR = Trader_Shaver('SHVR', 'MAB_SHVR', 0.00)
    self.MAB_SNPR = Trader_Sniper('SNPR', 'MAB_SNPR', 0.00)
    self.MAB_ZIP = Trader_ZIP('ZIP', 'MAB_ZIP', 0.00)
    ## Get all available traders count
    self.tradersNo = len(self.traders)

    # Initialise 'trade-ness' parameters
    self.mean = self.tradersNo * [self.earn]
    self.var = self.tradersNo * [self.uncertainty]

  # Get order, calculate trading price, and schedule
  def getorder( self, time, countdown, lob ):
    if len( self.orders ) < 1:
      order = None

    else:
      # Get order details
      price = self.orders[0].price
      orderType = self.orders[0].otype
      quantity = self.orders[0].qty

      # Do the magic...

      order = Order( self.tid, orderType, price, quantity, time )

    return order

  # Update trader's statistics based on current market situation
  def respond(self, time, lob, trade, verbose):
    True





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
