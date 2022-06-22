const template = document.createElement("template");

template.innerHTML = `
<div class="col-12 col-sm-12 col-md-6 col-lg-6 col-xl-6">
<div class="card text-white bg-secondary mb-3">
  <div class="card-header"></div>
  <div class="card-body d-flex justify-content-center align-items-center">
    <img
      style="min-height: 373px; max-height: 373px"
      class="img-fluid"
      src=""
    />
  </div>
</div>
</div>
`;


class Camera extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: "open" });
        this.shadowRoot.appendChild(template.content.cloneNode(true));

        this.shadowRoot.querySelector("card .card-header").innerHTML = this.getAttribute("stream");
        this.shadowRoot.querySelector("card img").src = this.getAttribute("img");
    }

    connectedCallback() {

    }

    disconnectedCallback() {

    }
}

window.customElements.define("camera", Camera);