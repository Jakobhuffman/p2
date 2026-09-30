#!/usr/bin/env python3

import os
import sys


def get_func_name(line):
    at_sign = line.find("@")
    open_parenthesis = line.find("(", at_sign)

    if at_sign == -1 or open_parenthesis == -1:
        return None

    return line[at_sign + 1:open_parenthesis].strip()


def get_func(lines):
    func = []
    func_name = None
    func_lines = []
    inside_func = False

    for line in lines:
        line = line.split(";", 1)[0].strip()

        if not inside_func:
            if line.startswith("define ") and "{" in line:
                func_name = get_func_name(line)
                func_lines = []
                inside_func = True
            continue

        if line == "}":
            func.append((func_name, func_lines))
            inside_func = False
        elif line != "":
            func_lines.append(line)

    return func


def is_call_instruction(instruction):
    instruction = instruction.strip()

    if "=" in instruction:
        instruction = instruction.split("=", 1)[1].strip()

    words = instruction.split()
    if len(words) == 0:
        return False

    if words[0] == "call":
        return True

    return (
        len(words) > 1
        and words[0] in ("tail", "musttail", "notail")
        and words[1] == "call"
    )


def get_blocks(function_lines):
    blocks = []
    labels = {}
    current_block = None

    for line in function_lines:
        if line.endswith(":"):
            label = line[:-1].strip()
            current_block = len(blocks)
            blocks.append([])
            labels[label] = current_block
        else:
            if current_block is None:
                current_block = len(blocks)
                blocks.append([])
                if current_block == 0:
                    labels["entry"] = current_block

            blocks[current_block].append(line)

            if is_call_instruction(line):
                current_block = None

    if len(blocks) == 0:
        blocks.append([])

    return blocks, labels


def get_br_labels(instruction):
    if not instruction.startswith("br "):
        return []

    words = instruction.replace(",", " ").split()
    br_labels = []

    for index in range(len(words) - 1):
        if words[index] == "label":
            label = words[index + 1]
            if label.startswith("%"):
                label = label[1:]
            br_labels.append(label)

    return br_labels


def get_edges(blocks, labels):
    edges = []

    for block_number in range(len(blocks)):
        block = blocks[block_number]
        if len(block) == 0:
            continue

        last_instruction = block[-1]

        if is_call_instruction(last_instruction):
            return_site = block_number + 1
            if return_site < len(blocks):
                edges.append((block_number, return_site, 0))
        else:
            br_labels = get_br_labels(last_instruction)

            for edge_number in range(len(br_labels)):
                label = br_labels[edge_number]
                if label in labels:
                    edges.append((block_number, labels[label], edge_number))

    return edges


def escape_record_label(text):
    escaped = ""

    for character in text:
        if character == "\\":
            escaped += "\\\\"
        elif character == '"':
            escaped += '\\"'
        elif character in "{}|<>":
            escaped += "\\" + character
        else:
            escaped += character

    return escaped


def make_block_label(block):
    if len(block) == 0:
        return ""

    escaped_instructions = []

    for instruction in block:
        escaped_instructions.append(escape_record_label(instruction))

    return "\\l".join(escaped_instructions) + "\\l"


def make_dot_graph(blocks, edges):
    lines = ["digraph {"]

    for block_number in range(len(blocks)):
        label = make_block_label(blocks[block_number])
        lines.append(
            '    Node{} [shape=record,label="{}"];'.format(block_number, label)
        )

    for source, destination, edge_number in edges:
        lines.append(
            "    Node{} -> Node{} [label={}];".format(
                source, destination, edge_number
            )
        )

    lines.append("}")
    return "\n".join(lines) + "\n"


def main():
    

    input_filename = sys.argv[1]
    

    with open(input_filename, "r", encoding="utf-8") as input_file:
        func = get_func(input_file.readlines())


    dots = []

    for func_name, after_name in func:
        blocks, labels = get_blocks(after_name)
        edges = get_edges(blocks, labels)
        dot = make_dot_graph(blocks, edges)
        output_filename = func_name + ".dot"

        with open(output_filename, "w", encoding="utf-8") as output_file:
            output_file.write(dot)

        dots.append(dot)

    if len(dots) == 1:
        print(dots[0], end="")

    return 0


if __name__ == "__main__":
    sys.exit(main())
