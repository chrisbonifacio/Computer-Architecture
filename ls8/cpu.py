"""CPU functionality."""

import sys

# Operations
binary_op = {
    0b00000001: 'HLT',
    0b10000010: 'LDI',
    0b01000111: 'PRN'
}

math_op = {
    "ADD": 0b10100000,
    "SUB": 0b10100001,
    "MUL": 0b10100010
}


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        # Registers
        self.reg = [0] * 8
        self.operand_a = None
        self.operand_b = None

        # Internal Registers
        self.pc = 0
        self.mar = None
        self.mdr = None
        self.instructions = {}
        self.instructions['HLT'] = self.halt
        self.instructions['LDI'] = self.load_int
        self.instructions['PRN'] = self.prn

    def halt(self):
        sys.exit()

    def load_int(self):
        self.reg[self.operand_a] = self.operand_b

    def prn(self):
        print(self.reg[self.operand_a])

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

    def alu(self, op, reg_a, reg_b):
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

            # TODO --- if arithmathetic bit is on, run math operation

            if (IR << 2) % 255 >> 7 == 1:
                self.alu(IR, self.operand_a, self.operand_b)
                self.move_pc(IR)

            elif (IR << 2) % 255 >> 7 == 0:
                self.instructions[binary_op[IR]]()
                self.move_pc(IR)

            else:
                print(f"I did not understand that command: {IR}")
                print(self.trace())
                sys.exit(1)

        # after running code for any particular instruction, the PC needs to be updated to point to the next instruction for the next iteration of the loop in run()
