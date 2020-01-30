import osbrain
from osbrain import Agent
import tables as tb
import time

class ka_base(Agent):
  """Base agent to define __init__ and basic functions"""

  def on_init(self):
    # This connects to the blackboard and is used to signal when the agent needs to write 
    # to the blackboard, this is a reply-requestion communication
    self.connect(self.bb_addr(self.bb_permission_alias), alias=self.bb_permission_alias)
    # This connects to the blackboard. When the blackboard sends the agent a message via the run_opt alias, 
    # it will trigger the simulate method as the handler to solve the problem
    self.connect(self.bb_addr(self.bb_opt_alias), alias=self.bb_opt_alias, handler='simulate')
    self.bind('PUSH', alias='run_next_opt')
    self.root = '/{}'.format(self.name)
    self.db_entry = []
    self.doubled = 0
    self.val = 0
    db = tb.open_file("blackboard_db", "a")
    db.create_group(db.root, self.name)
    db.close()

  def write_to_db(self):
    # Open the database and check if the result has already been submitted.
    # If it has, don't write to DB
    with tb.open_file("blackboard_db", "a") as db:
      for node in db:
        if 'Val_{}'.format(self.val) in node:
          break
      else:
        db.create_array(self.root, 'Val_{}'.format(self.val), [self.doubled])

  def ask_permission_to_write(self):
    """Create a loop and continually check to determine if we can write to the database"""
    can_send = False
    while can_send == False:
      #Ask BB if agent can write to BB
      self.send(self.bb_permission_alias, self.name)
      can_send = self.recv(self.bb_permission_alias)
      time.sleep(0.5)
    self.write_to_db()

  def simulate(self, i):
    pass

  def squared(self, x):
    self.val = x
    return x * x

  def ask_bb(self):
    """Let the Blackboard know the agent is ready to solve another problem"""
    self.send('run_next_opt', self)    