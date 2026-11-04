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

  //Butacas: no se pueden elegir más butacas que entradas, y se cuenta cuántas van
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
      if (maximo > 0) {
        contador.textContent = "Elegidas: " + elegidas + " de " + maximo;
        continuar.disabled = elegidas !== maximo;
      } else {
        contador.textContent = "Elegidas: " + elegidas;
      }
    }

    checkboxes.forEach(function (checkbox) {
      checkbox.addEventListener("change", function () {
        if (maximo > 0 && contarElegidas() > maximo) {
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
      const base = parseInt(formulario.dataset.total, 10) || 0;
      const campos = formulario.querySelectorAll("input[data-precio]");

      function calcular() {
        let total = base;
        campos.forEach(function (campo) {
          const cantidad = parseInt(campo.value, 10) || 0;
          total = total + cantidad * parseInt(campo.dataset.precio, 10);
        });
        salida.textContent = "$" + total;
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

  //Cuando la página termina de cargar, activamos todo
  document.addEventListener("DOMContentLoaded", function () {
    iniciarMenu();
    iniciarDesplegables();
    iniciarCarruseles();
    iniciarMostrarPassword();
    iniciarButacas();
    iniciarTotalEnVivo();
    iniciarConfirmaciones();
  });
})();
