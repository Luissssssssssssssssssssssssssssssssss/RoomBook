let salaAtual = null;

// =======================
// SELECIONAR SALA
// =======================
function selecionarSala(nomeSala) {
    salaAtual = nomeSala;
    document.getElementById("salaSelecionada").innerText = nomeSala;
}

// =======================
// ABRIR MODAL
// =======================
function abrirReserva(hora, dia) {
    if (!salaAtual) {
        alert("Selecione uma sala primeiro!");
        return;
    }

    document.getElementById("modalSala").innerText = salaAtual;
    document.getElementById("modalDia").innerText = dia;
    document.getElementById("modalHora").innerText = hora;

    const modal = new bootstrap.Modal(
        document.getElementById("modalReserva")
    );
    modal.show();
}

// =======================
// CONFIRMAR RESERVA
// =======================
function confirmarReserva() {
    const sala = document.getElementById("modalSala").innerText;
    const dia = document.getElementById("modalDia").innerText;
    const hora = document.getElementById("modalHora").innerText;
    const nome = document.getElementById("nomeReserva").value;

    if (!nome) {
        alert("Informe o nome da reserva");
        return;
    }

    // Dia da semana → data real (simples)
    const hoje = new Date();
    const dias = { Seg: 1, Ter: 2, Qua: 3, Qui: 4, Sex: 5 };
    const diff = dias[dia] - hoje.getDay();
    const data = new Date(hoje);
    data.setDate(hoje.getDate() + diff);

    const dataFormatada = data.toISOString().split("T")[0];

    const hora_inicio = hora;
    const hora_fim = (parseInt(hora.split(":")[0]) + 1) + ":00";

    const formData = new FormData();
    formData.append("sala", sala);
    formData.append("data", dataFormatada);
    formData.append("hora_inicio", hora_inicio);
    formData.append("hora_fim", hora_fim);

    fetch("/agendar", {
        method: "POST",
        body: formData
    })
    .then(res => {
        if (res.redirected) {
            window.location.href = res.url;
        }
    });
}
function cancelarReserva(sala, data, horario) {
    if (!confirm("Deseja cancelar esta reserva?")) return;

    const formData = new FormData();
    formData.append("sala", sala);
    formData.append("data", data);
    formData.append("horario", horario);

    fetch("/cancelar", {
        method: "POST",
        body: formData
    }).then(() => location.reload());
}
function cancelarReserva(sala, data, horario) {
    if (!confirm("Deseja cancelar esta reserva?")) return;

    const formData = new FormData();
    formData.append("sala", sala);
    formData.append("data", data);
    formData.append("horario", horario);

    fetch("/cancelar", {
        method: "POST",
        body: formData
    }).then(() => location.reload());
}
