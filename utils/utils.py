def preparar_input_avaliacao(input_data):
    if isinstance(input_data, list):
        return "\n".join(
            f"Turno {i + 1}: {turno}"
            for i, turno in enumerate(input_data)
        )

    return input_data