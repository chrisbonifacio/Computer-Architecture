"""CPU functionality."""

import sys

# Operation Tables
binary_op = {
    0b00000001: 'HLT',
    0b10000010: 'LDI',
    0b01000111: 'PRN',
    0b01000101: 'PUSH',
    0b01000110: 'POP',
    0b01010000: 'CALL',
    0b00010001: 'RET'
}

math_op = {
    "ADD": 0b10100000,
    "SUB": 0b10100001,
    "MUL": 0b10100010
}

# Global Constants
SP = 7  # Stack Pointer


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        # Registers
        self.reg = [0] * 8
        self.reg[SP] = 0xF4
        self.operand_a = None
        self.operand_b = None

        # Internal Registers
        self.pc = 0  # Program Counter
        self.mar = None  # Memory Address Register
        self.mdr = None  # Memory Data Register

        # Branch Table
        self.instructions = {}
        self.instructions['HLT'] = self.HALT
        self.instructions['LDI'] = self.LOAD
        self.instructions['PRN'] = self.PRINT
        self.instructions['PUSH'] = self.PUSH
        self.instructions['POP'] = self.POP
        self.instructions['CALL'] = self.CALL
        self.instructions['RET'] = self.RET

    def CALL(self):
        """Calls a subroutine (function) at the address stored in the register."""
        self.reg[SP] -= 1

        # address of the instruction
        instruction_address = self.pc + 2

        # pushing the address of the instruction onto the stack
        self.ram[self.reg[SP]] = instruction_address

        # PC is set to the address stored in the register
        register = self.operand_a

        self.pc = self.reg[register]

    def RET(self):
        self.pc = self.ram[self.reg[SP]]

        self.reg[SP] += 1

    def HALT(self):
        """Exit the current program"""
        sys.exit()

    def LOAD(self):
        """Load value to register"""
        self.reg[self.operand_a] = self.operand_b

    def PRINT(self):
        """Print the value in a register"""
        print(self.reg[self.operand_a])

    def PUSH(self):
        """Push the value in the given register to the top of the stack"""
        # decrement the SP
        global SP

        self.reg[SP] -= 1

        # copy the value in the given register to the address pointed to by SP
        value = self.reg[self.operand_a]

        self.ram[self.reg[SP]] = value

    def POP(self):
        """Pop the value at the top of the stack into the given register"""
        global SP
        # copy the value from the address pointed to by SP to the given register

        # value at the address pointed to by SP
        value = self.ram[self.reg[SP]]

        # given register from argument
        register = self.operand_a

        # copying the value from memory to the given register
        self.reg[register] = value

        # increment SP
        self.reg[SP] += 1

    def ram_read(self, address):
        """Accepts an address to read and returns the value stored there"""
        self.mar = address
        self.mdr = self.ram[address]
        return self.ram[address]

    def ram_write(self, value, address):
        """Accepts a value to write, and the address to write it to"""
        self.mar = address
        self.mdr = value
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""

        if len(sys.argv) != 2:
            print("ERROR: Must have file name")
            sys.exit(1)

        filename = sys.argv[1]

        try:
            address = 0
            # Open the file
            with open(filename) as program:
                # Read all the lines
                for instruction in program:
                    # Parse out comments
                    comment_split = instruction.strip().split("#")

                    # Cast the numbers from strings to ints
                    value = comment_split[0].strip()

                    # Ignore blank lines
                    if value == "":
                        continue

                    num = int(value, 2)
                    self.ram[address] = num
                    address += 1

        except FileNotFoundError:
            print("File not found")
            sys.exit(2)

    def ALU(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == math_op["ADD"]:
            self.reg[reg_a] += self.reg[reg_b]

        elif op == math_op["SUB"]:
            self.reg[reg_a] -= self.reg[reg_b]

        elif op == math_op["MUL"]:
            self.reg[reg_a] *= self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

    def move_pc(self, IR):
        """Accepts an Instruction Register.\n
        Increments the PC by the number of arguments returned by the IR."""
        if (IR << 3) % 255 >> 7 != 1:
            self.pc += (IR >> 6) + 1

    def run(self):
        """Run the CPU."""
        while True:
            # read the memory address that's stored in register PC,
            # store that result in IR (Instruction Register).
            # This can just be a local variable
            IR = self.ram_read(self.pc)

            # using ram_read(), read the bytes at PC+1 and PC+2 from RAM into variables
            self.operand_a = self.ram_read(self.pc + 1)
            self.operand_b = self.ram_read(self.pc + 2)

            # depending on the value of the opcode, perform the actions needed for the instruction

            # if arithmathetic bit is on, run math operation
            if (IR << 2) % 255 >> 7 == 1:
                self.ALU(IR, self.operand_a, self.operand_b)
                self.move_pc(IR)

            # else, run basic operations
            elif (IR << 2) % 255 >> 7 == 0:
                self.instructions[binary_op[IR]]()
                self.move_pc(IR)

            # if instruction is unrecognized, exit
            else:
                print(f"I did not understand that command: {IR}")
                print(self.trace())
                sys.exit(1)

        # after running code for any particular instruction, the PC needs to be updated to point to the next instruction for the next iteration of the loop in run()
