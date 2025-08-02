function consultarRut() {
    const rut = document.getElementById('rutInput').value;
    fetch(`/consultar-rut/?rut=${rut}`)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'encontrado') {
                alert(`RUT corresponde a tipo: ${data.tipo}`);
            } else if (data.status === 'no_encontrado') {
                alert("RUT no se encuentra registrado.");
            } else {
                alert("Error en la solicitud.");
            }
        });
}
