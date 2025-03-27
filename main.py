import pygame
import random
import time
import logging
from node import Node, NodeState
from node_network import NodeNetwork
from enemy import Enemy
from events import *
from animations import HeartbeatAnimation, TextAnimation

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(message)s',
                   datefmt='%H:%M:%S')

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("RAFT Heartbeat Visualization")
    clock = pygame.time.Clock()

    # Create nodes
    nodes = []
    nodesNum = 5
    for i in range(nodesNum):
        x = random.randint(100, 700)
        y = random.randint(100, 500)
        node = Node(i, x, y, 30, nodesNum)
        nodes.append(node)

    # Start all node threads
    for node in nodes:
        node.start()

    # Set initial leader
    nodes[0].state = NodeState.LEADER
    nodes[0].last_heartbeat = time.time()

    # Create enemies
    enemies = []
    for _ in range(10):
        x = random.randint(0, 800)
        y = random.randint(0, 600)
        enemies.append(Enemy(x, y))

    # Animation list
    animations = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == HEARTBEAT_SENT:
                # Create heartbeat animation
                animations.append(
                    HeartbeatAnimation(event.from_x, event.from_y)
                )
                logging.info(f"Heartbeat sent from {event.from_id} TERM {event.term}")
                # Handle heartbeat in all nodes
                for node in nodes:
                    node.handle_heartbeat(event.from_id, event.term)
            elif event.type == HEARTBEAT_RECEIVED:
                # Handle vote request in all nodes
                animations.append(
                    TextAnimation(event.from_x, event.from_y - 20)
                )
                logging.info(f"Heartbeat received from {event.from_id} TERM {event.term}")
            elif event.type == VOTE_REQUEST:
                # Handle vote request in all nodes
                print(f"Vote request received from {event.candidate_id}")
                for node in nodes:
                    if node.id == event.candidate_id:
                        continue
                    else:
                        node.handle_vote_request(event.candidate_id, event.term)
            elif event.type == VOTE_RESPONSE:
                # Handle vote granted in all nodes
                print(f"Vote granted to {event.candidate_id} by {event.voter_id}")
                for node in nodes:
                    if node.id == event.candidate_id:
                        
                        node.handle_vote_response(event.voter_id, event.candidate_id, event.term)
            elif event.type == ELECTION_COMPLETE:
                # Handle election complete in all nodes
                for node in nodes:
                    if node.id == event.leader_id:
                        leader = node
                print(f"Election complete, leader is {event.leader_id}")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for node in nodes:
                    dx = node.x + node.size/2 - mouse_x
                    dy = node.y + node.size/2 - mouse_y
                    if (dx ** 2 + dy ** 2) ** 0.5 < node.size/2:
                        node.handle_click()
                        break

        screen.fill((255, 255, 255))

        # Find current leader
        leader = next((node for node in nodes if node.state == NodeState.LEADER), None)

        # Update and draw enemies
        if leader:
            for enemy in enemies:
                enemy.move_towards(leader)
                enemy.draw(screen)
                
                # Check collision with leader
                dx = leader.x + leader.size/2 - enemy.x
                dy = leader.y + leader.size/2 - enemy.y
                distance = (dx ** 2 + dy ** 2) ** 0.5
                
                if distance < (leader.size/2 + enemy.size):
                    leader.health = leader.health - 0.5
                    if leader.health <= 0:
                        leader.state = NodeState.DEAD
                        leader.is_active = False
                        leader = None
                        break

        # Draw nodes
        for node in nodes:
            node.draw(screen)

        # Update and draw animations
        animations = [
            anim for anim in animations 
            if anim.draw(screen)
        ]

        # Draw leader's health bar if exists
        if leader:
            pygame.draw.rect(screen, (255, 0, 0),
                           (leader.x, leader.y - 10, 
                            leader.size * (leader.health/100), 5))

        pygame.display.flip()
        clock.tick(60)

    # Clean up
    for node in nodes:
        node.stop()
        node.join()
    pygame.quit()

if __name__ == "__main__":
    main()

