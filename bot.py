import discord
import secrets
import programs

from Turing import mpcall, c_fifo_mpcall, parse_command

class TuringBot (discord.Client):
    
    def __init__(self):
        super().__init__(intents = discord.Intents(
            guilds         = True,
            guild_messages = True
        ))

    async def on_ready(self):
        print("Turing: Running...")

    async def on_message(self, event):
        if event.author == self.user: return

        author  = event.author
        message = event.content
        channel = event.channel
        
        if (parsed := parse_command(message)):

            print("=== [Descriptor] ===")

            program_name, file_type, code = parsed

            if program_name in programs.stream.keys():
                program_path = programs.stream[program_name]

                is_fifo = False

            if program_name in programs.fifo.keys():
                program_path = programs.fifo[program_name]

                is_fifo = True

            print(f"User '{author}' requested '{program_name}' execution:\n```\n{code}\n```")

            if not program_path:

                print(f"Program '{program_name}' is not a valid program.")

                await channel.send(f"```diff\n- Program '{program_name}' is not a valid program.\n```")

                return

            if is_fifo:

                fifo_name = f"_fifo_{program_name}.{file_type}"

                if (output := c_fifo_mpcall(program_path, [fifo_name], 5, fifo_name, code)):

                    program_out, decor_type = (output.stderr, '-') if output.returncode else (output.stdout, '+')
                    program_out = program_out.decode()

                    print(f"Execution @ '{program_name}' yields ({output.returncode}):\n```\n{program_out}\n```")

                    await channel.send(f"```diff\n{decor_type} Exit @ '{program_name}' yields ({output.returncode}).\n```")
                    await channel.send(f"```{file_type}\n{program_out}\n```")

                    return

                print(f"Timed out.")

                await channel.send(f"```diff\n- Operation halts!\n```")

                return

            if (output := mpcall(program_path, [code], 5)):
                program_out, decor_type = (output.stderr, '-') if output.returncode else (output.stdout, '+')
                program_out = program_out.decode()

                print(f"Execution @ '{program_name}' yields ({output.returncode}):\n```\n{program_out}\n```")

                await channel.send(f"```diff\n{decor_type} Exit @ '{program_name}' yields ({output.returncode}).\n```")
                await channel.send(f"```{file_type}\n{program_out}\n```")

                return

            print("Timed out.")
            
            await channel.send(f"```diff\n- Operation halts!\n```")

            return

if __name__ == "__main__" \
    : TuringBot().run(secrets.AUTH_TOKEN) ; exit(0)
