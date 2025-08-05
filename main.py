"""Example usage of the Kagenti A2A Client."""

from kagenti_a2a_client import SyncClient, SyncClientError


def main():
    """Demonstrate basic usage of the Kagenti A2A client."""
    
    # Example agent URL (replace with actual kagenti agent endpoint)
    agent_url = "http://localhost:8080"  # Example URL
    
    print("Kagenti A2A Client Example")
    print("=" * 30)
    
    # Create client
    try:
        with SyncClient(agent_url=agent_url, timeout=10.0) as client:
            
            # Check agent health
            print("Checking agent health...")
            if client.health_check():
                print("✓ Agent is healthy")
            else:
                print("✗ Agent is not responding")
                return
            
            # Create a new session
            print("\nCreating new session...")
            session = client.create_session()
            print(f"✓ Created session: {session.session_id}")
            
            # Send a message
            print("\nSending message to agent...")
            try:
                response = client.send_message(
                    message="Hello! Can you help me understand how A2A protocol works?",
                    session_id=session.session_id
                )
                
                print(f"✓ Agent response:")
                print(f"  Status: {response.status}")
                print(f"  Output: {response.output}")
                
                # Send follow-up message
                print("\nSending follow-up message...")
                response2 = client.send_message(
                    message="Can you give me a specific example?",
                    session_id=session.session_id
                )
                
                print(f"✓ Agent response:")
                print(f"  Status: {response2.status}")
                print(f"  Output: {response2.output}")
                
                # Show conversation history
                print("\nConversation history:")
                history = client.get_conversation_history(session.session_id)
                for i, turn in enumerate(history, 1):
                    print(f"  Turn {i}:")
                    print(f"    User: {turn.input_text}")
                    print(f"    Agent: {turn.output_text}")
                    if turn.error:
                        print(f"    Error: {turn.error}")
                
            except SyncClientError as e:
                print(f"✗ Client error: {e}")
            
            # List active sessions
            print(f"\nActive sessions: {client.list_sessions()}")
            
            # Clean up
            print("\nClosing session...")
            client.close_session(session.session_id)
            print("✓ Session closed")
    
    except SyncClientError as e:
        print(f"✗ Failed to create client: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


if __name__ == "__main__":
    main()
