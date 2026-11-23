(function () {
  "use strict";

  function iniciarMenu() {
    const boton = document.getElementById("boton-menu");
    const menu = document.getElementById("menu-principal");
    if (!boton || !menu) {
      return;
    }
    boton.addEventListener("click", function () {
      menu.classList.toggle("abierto");
    });
  }

  function iniciarCarruseles() {
    const cajas = document.querySelectorAll("[data-carrusel]");
    cajas.forEach(function (caja) {
      const carrusel = caja.querySelector(".carrusel");
      const anterior = caja.querySelector("[data-carrusel-anterior]");
      const siguiente = caja.querySelector("[data-carrusel-siguiente]");

      function mover(direccion) {
        carrusel.scrollBy({ left: direccion * carrusel.clientWidth * 0.9, behavior: "smooth" });
      }

      anterior.addEventListener("click", function () { mover(-1); });
      siguiente.addEventListener("click", function () { mover(1); });
    });
  }

  function iniciarMostrarPassword() {
    const botones = document.querySelectorAll("[data-mostrar-password]");
    botones.forEach(function (boton) {
      const campo = document.getElementById(boton.dataset.mostrarPassword);
      boton.addEventListener("click", function () {
        const estaOculta = campo.type === "password";
        campo.type = estaOculta ? "text" : "password";
        boton.textContent = estaOculta ? "Ocultar" : "Mostrar";
      });
    });
  }

  function iniciarButacas() {
    const formulario = document.querySelector("[data-max-butacas]");
    if (!formulario) {
      return;
    }
    const maximo = parseInt(formulario.dataset.maxButacas, 10);
    const contador = document.getElementById("contador-butacas");
    const continuar = document.getElementById("boton-continuar");
    const checkboxes = formulario.querySelectorAll("input[name='butacas']");

    function contarElegidas() {
      return formulario.querySelectorAll("input[name='butacas']:checked").length;
    }

    function actualizar() {
      const elegidas = contarElegidas();
      contador.textContent = "Elegidas: " + elegidas + " de " + maximo;
      continuar.disabled = elegidas !== maximo;  
    }

    checkboxes.forEach(function (checkbox) {
      checkbox.addEventListener("change", function () {
        if (contarElegidas() > maximo) {
          checkbox.checked = false;  
        }
        actualizar();
      });
    });

    actualizar();
  }

  function iniciarTotalEnVivo() {
    const formularios = document.querySelectorAll("[data-total]");
    formularios.forEach(function (formulario) {
      const salida = formulario.querySelector("[data-total-salida]");
      const base = parseFloat(formulario.dataset.total) || 0;
      const campos = formulario.querySelectorAll("input[data-precio]");

      function calcular() {
        let total = base;
        campos.forEach(function (campo) {
          const cantidad = parseInt(campo.value, 10) || 0;
          total = total + cantidad * parseFloat(campo.dataset.precio);
        });
        salida.textContent = "$" + total.toLocaleString("es-AR");
      }

      campos.forEach(function (campo) {
        campo.addEventListener("input", calcular);
      });
      calcular();
    });
  }

  function iniciarConfirmaciones() {
    const formularios = document.querySelectorAll("form[data-confirmar]");
    formularios.forEach(function (formulario) {
      formulario.addEventListener("submit", function (evento) {
        if (!window.confirm(formulario.dataset.confirmar)) {
          evento.preventDefault();  
        }
      });
    });
  }
  function iniciarEscanerQR() {
    const readerDiv = document.getElementById("reader");
    
    if (!readerDiv) return; 

    const html5QrCode = new Html5Qrcode("reader");
    let escaneando = true;

    function onScanSuccess(decodedText, decodedResult) {
        if (!escaneando) return; 
        escaneando = false;

        document.getElementById('qr_codigo_input').value = decodedText;
        
        document.getElementById('formQR').submit();
    }

    Html5Qrcode.getCameras().then(devices => {
        if (devices && devices.length) {
            html5QrCode.start(
                { facingMode: "environment" }, 
                { fps: 10, qrbox: 250 },
                onScanSuccess
            );
        }
    }).catch(err => {
        readerDiv.innerHTML = "<p class='chico texto-rojo'>No se pudo acceder a la cámara. Verificá los permisos del navegador.</p>";
    });
  }
  
  document.addEventListener("DOMContentLoaded", function () {
    iniciarMenu();
    iniciarCarruseles();
    iniciarMostrarPassword();
    iniciarButacas();
    iniciarTotalEnVivo();
    iniciarConfirmaciones();
    iniciarEscanerQR(); 
  });
})();
