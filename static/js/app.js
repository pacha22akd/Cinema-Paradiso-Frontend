(function () {
  "use strict";

  //Menú de celular: el botón ☰ abre y cierra el menú
  function iniciarMenu() {
    const boton = document.getElementById("boton-menu");
    const menu = document.getElementById("menu-principal");
    if (!boton || !menu) {
      return;
    }
    boton.addEventListener("click", function () {
      const abierto = menu.classList.toggle("abierto");
      boton.setAttribute("aria-expanded", abierto ? "true" : "false");
    });
  }

  //El selector de cines (de la barra superior) se cierra al hacer click afuera
  function iniciarDesplegables() {
    document.addEventListener("click", function (evento) {
      const abiertos = document.querySelectorAll(".desplegable[open]");
      abiertos.forEach(function (desplegable) {
        if (!desplegable.contains(evento.target)) {
          desplegable.removeAttribute("open");
        }
      });
    });
  }

  //Carruseles: las flechas ‹ › mueven el carrusel
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

  //Login: botón para mostrar u ocultar la contraseña
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

  //Butacas: hay que elegir exactamente tantas como entradas (data-max-butacas), y se cuenta cuántas van
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
      continuar.disabled = elegidas !== maximo;  // hasta completar todas las butacas no se puede seguir
    }

    checkboxes.forEach(function (checkbox) {
      checkbox.addEventListener("change", function () {
        if (contarElegidas() > maximo) {
          checkbox.checked = false;  // se pasó del máximo: desmarcamos la última
        }
        actualizar();
      });
    });

    actualizar();
  }

  //Total en vivo: suma cantidad x precio mientras el usuario cambia los números
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

  //Formularios con pregunta de confirmación (por ejemplo, cancelar una entrada)
  function iniciarConfirmaciones() {
    const formularios = document.querySelectorAll("form[data-confirmar]");
    formularios.forEach(function (formulario) {
      formulario.addEventListener("submit", function (evento) {
        if (!window.confirm(formulario.dataset.confirmar)) {
          evento.preventDefault();  // si dice que no, el formulario no se envía
        }
      });
    });
  }
  function iniciarEscanerQR() {
    const readerDiv = document.getElementById("reader");
    
    // Si no estamos en la página del escáner, no hacemos nada
    if (!readerDiv) return; 

    const html5QrCode = new Html5Qrcode("reader");
    let escaneando = true;

    function onScanSuccess(decodedText, decodedResult) {
        if (!escaneando) return; 
        escaneando = false;

        // Ponemos el texto del QR en el input oculto
        document.getElementById('qr_codigo_input').value = decodedText;
        
        // Enviamos el formulario automáticamente al servidor Flask
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
  
  //Cuando la página termina de cargar, activamos todo
  document.addEventListener("DOMContentLoaded", function () {
    iniciarMenu();
    iniciarDesplegables();
    iniciarCarruseles();
    iniciarMostrarPassword();
    iniciarButacas();
    iniciarTotalEnVivo();
    iniciarConfirmaciones();
    iniciarEscanerQR(); 
  });
})();
