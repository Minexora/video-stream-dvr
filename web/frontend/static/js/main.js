document.addEventListener("DOMContentLoaded", function (event) {
    // var player = videojs('#video-player');
    // player.play()

    // let add_camera_btn = document.getElementById("add_camera_btn");
    // add_camera_btn.addEventListener("click", function (event) {

    //     let payload = {
    //         "camera_name": document.getElementById("camera_name").value,
    //         "camera_url": document.getElementById("camera_url").value,
    //     }
    //     axios.post("/add-camera", payload).then(function (response) {
    //         console.log(response)
    //     })
    // });
    var socket = io("127.0.0.1:8080");

    let add_camera_btn = document.getElementById("add_camera_btn");
    add_camera_btn.addEventListener("click", function (event) {
        let payload = {
            "camera_name": document.getElementById("camera_name").value,
            "camera_url": document.getElementById("camera_url").value,
        }
        socket.emit("add_camera", payload);
    });

    socket.on("connect", function () {
        console.log(`BAĞLANDIN: ${socket.id}`);
        const video_streams = document.querySelector('.video_streams');
        video_streams.innerHTML = ""
        socket.emit("add_ui");
    });

    socket.on("on_add_camera_result", function (data) {
        console.log(`on_add_camera_result: ${JSON.stringify(data, null, 2)}`);
        if (data.status && data.data.camera_name) {
            const video_streams = document.querySelector('.video_streams');
            const div = document.createElement('div')
            div.classList = "col-12 col-sm-12 col-md-6 col-lg-6 col-xl-6"
            div.id = `${data.data.camera_name}`
            video_streams.style.cssText = "-ms-overflow-style: none !important;scrollbar-width: none!important;overflow-y: scroll!important; height: calc(100vh - 120px);overflow: -moz-scrollbars-none;"
            div.innerHTML += `
                <div class="card text-white bg-secondary mb-3">
                <div class="card-header">${data.data.camera_name}</div>
                <div class="card-body d-flex justify-content-center align-items-center">
                <img
                    style="min-height: 373px; max-height: 373px"
                    class="img-fluid"
                    src=""
                />
                </div>
                </div>
            `;
            video_streams.appendChild(div)
            closeModal();
            if ("img" in data.data) {
                const img = document.querySelector(`#${data.data.camera_name} img`)
                img.src = data.data.img
            }
        }
        else {
            toastStart('HATA', data.msg);
            closeModal();
        }
    });

    socket.on("on_video_picture", function (data) {
        const img = document.querySelector(`#${data.data.camera_name} img`)
        img.src = data.data.img
    });

    socket.on("disconnect", function () {
        console.log(`BAĞLANTI KESİNDİ`);
    });


    function toastStart(header = "", content = "") {
        const toast_ = document.getElementById('msgToast')
        toast_.querySelector(".header").innerHTML = header
        toast_.querySelector(".toast-body").innerHTML = content
        if (toast_) {

            const toast_div = new bootstrap.Toast(toast_)
            toast_div.show()
        }
    }

    function closeModal() {
        const modal_div = document.getElementById('addCameraModal');
        modal_div.classList.add("hide");
        modal_div.classList.remove("show")
        modal_div.style.display = 'none';
        modal_div.setAttribute('aria-hidden', 'true');
    }
})