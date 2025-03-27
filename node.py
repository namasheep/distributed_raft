import pygame
import random
import time
import logging
from enum import Enum
from events import *
import threading

class NodeState(Enum):
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3

class Node(threading.Thread):
    def __init__(self, id, x, y, size):
        threading.Thread.__init__(self)
        self.id = id
        self.x = x
        self.y = y
        self.size = size
        self.state = NodeState.FOLLOWER
        self.health = 100
        self.term = 0
        self.votes_received = 0
        self.election_timeout = random.uniform(1.5, 3.0)
        self.last_heartbeat = time.time()
        self.voted_for = None
        
        # Log-related attributes
        self.commit_log = []
        self.pending_log = None
        self.last_committed_index = -1
        self.is_active = True
        self.running = True
        
        # Thread-safe locks
        self.state_lock = threading.Lock()
        self.log_lock = threading.Lock()
        
    def run(self):
        """Main thread loop for node"""
        while self.running:
            current_time = time.time()
            
            with self.state_lock:
                if self.is_active:
                    # Leader sends heartbeats
                    if self.state == NodeState.LEADER:
                        if current_time - self.last_heartbeat >= 10:  # Heartbeat interval
                            self.send_heartbeat()
                            self.last_heartbeat = current_time
                    
                    # Followers check for election timeout
                    elif self.state == NodeState.FOLLOWER:
                        if current_time - self.last_heartbeat >= self.election_timeout:
                            self.start_election()
            
            time.sleep(0.01)


    def handle_heartbeat(self, from_id, term):
        """Handle heartbeat from another node"""
        with self.state_lock:
            if self.state == NodeState.FOLLOWER:
                self.last_heartbeat = time.time()
                self.is_active = True
                event = pygame.event.Event(HEARTBEAT_RECEIVED, {
                    'from_id': from_id,
                    'term': term,
                    'from_x': self.x,
                    'from_y': self.y
                })
                pygame.event.post(event)
            elif self.state == NodeState.CANDIDATE:
                self.last_heartbeat = time.time()
            elif self.state == NodeState.LEADER:
                self.last_heartbeat = time.time()

            """if term > self.term:
                self.term = term
                self.state = NodeState.FOLLOWER
                self.voted_for = None
            """
            # Log the heartbeat
           
            
    
    def send_heartbeat(self):
        """Send heartbeat to all nodes"""
        event = pygame.event.Event(HEARTBEAT_SENT, {
            'from_id': self.id,
            'term': self.term,
            'from_x': self.x + self.size/2,
            'from_y': self.y + self.size/2
        })
        pygame.event.post(event)

    def start_election(self):
        """Start an election"""
        with self.state_lock:
            self.state = NodeState.CANDIDATE
            self.term += 1
            self.votes_received = 1  # Vote for self
            self.voted_for = self.id
            
            # Send vote request
            event = pygame.event.Event(VOTE_REQUEST, {
                'candidate_id': self.id,
                'term': self.term
            })
            pygame.event.post(event)

    def stop(self):
        """Stop the node thread"""
        self.running = False

    def draw(self, screen):
        """Draw node on screen"""
        with self.state_lock:
            base_color = (0, 255, 0) if self.state == NodeState.LEADER else \
                        (255, 165, 0) if self.state == NodeState.CANDIDATE else \
                        (0, 0, 255)
            color = base_color if self.is_active else tuple(c // 2 for c in base_color)
            pygame.draw.rect(screen, color, (self.x, self.y, self.size, self.size))
