const uploadForm = document.getElementById('upload-form')
const input = document.getElementById('id_video_file')
console.log(input)

const alertBox = document.getElementById('alert-box')
const videoBox = document.getElementById('video-box')
const progressBox = document.getElementById('progress-box')
const cancelBox = document.getElementById('cancel-box')
const cancelBtn = document.getElementById('cancel-btn')
const checkBox = document.getElementById('check-box')
const uploadBox = document.getElementById('upload-box')


const csrf = document.getElementsByName('csrfmiddlewaretoken')



input.addEventListener('change', ()=>{
    const video_data = input.files[0]
    const video_size = (video_data.size / 1024 / 1024).toFixed(2)
    console.log(video_size)

    if (video_size > 99 || video_size < 0.1) {
        alert("File must be between the size of 2-100 MB")
    } else {
        uploadBox.classList.remove('not-visible')

        const url = URL.createObjectURL(video_data)
        videoBox.innerHTML = `<video class="video" id="video-element" src="${url}" poster="${url}" type="video/mp4" autoplay muted loop></video>`

        //var video = document.getElementById('video');
        
        $("#upload-btn").off('click').on("click", function() {
            progressBox.classList.remove('not-visible')
            cancelBox.classList.remove('not-visible')
            //$("#upload-btn").attr({ "disabled": true });
            uploadBox.classList.add('not-visible')

            const fd = new FormData()
            fd.append('csrfmiddlewaretoken', csrf[0].value)
            fd.append('video_file', video_data) // modelsの変数名（video_file）
            //fd.append('thumbnail', img_data)
        
            $.ajax({
                type:'POST',
                url: uploadForm.action,
                enctype: 'multipart/form-data',
                data: fd,
                beforeSend: function(){
                    console.log('before')
                    alertBox.innerHTML = ""
                },
                xhr: function(){
                    const xhr = new window.XMLHttpRequest();
                    xhr.upload.addEventListener('progress', e=>{
                        // console.log(e)
                        if (e.lengthComputable) {
                            const percent = e.loaded /e.total * 100
                            console.log(percent)
                            if (percent === 100){
                                progressBox.innerHTML = '<div class="progress"><div class="indeterminate"></div>'
                            
                                
                            }
                            else {
                                progressBox.innerHTML = `<div class="progress">
                                                            <div class="progress-bar" role="progressbar" style="width: ${percent}%" aria-valuenow="${percent}" aria-valuemin="0" aria-valuemax="100"></div>
                                                        </div>
                                                        <p>${percent.toFixed(1)}%</p>`
                            }
                        }
                    })
                    cancelBtn.addEventListener('click', ()=>{
                        xhr.abort()
                        setTimeout(()=>{
                            uploadForm.reset()
                            progressBox.innerHTML = ""
                            alertBox.innerHTML = ""
                            cancelBox.classList.add('not-visible')
                        }, 2000)
                        
                    })
                    return xhr
                },
                success: function(response){
                    console.log(response)
                    //videoBox.innerHTML = `<video class="video" src="${url}" poster="${url}" type="video/mp4" autoplay muted loop></video>`
                    alertBox.innerHTML = `<div class="card-alert card green lighten-4 green-text text-darken-4 text-center" role="alert">
                                            <strong>
                                                Video uploaded! ${video_size} MB
                                            </strong>
                                        </div>`
                    uploadBox.classList.add('not-visible')
                    cancelBox.classList.add('not-visible')
                    progressBox.innerHTML = ""
                    uploadForm.innerHTML = ""
                    $('.card-alert > button').on('click', function(){
                        $(this).closest('div.card-alert').fadeOut('slow');
                    })
                    checkBox.classList.remove('not-visible')
                },
                error: function(error){
                    console.log(error)
                    alertBox.innerHTML = `<div class="alert card red lighten-4 red-text text-darken-4" role="alert">
                                            Something went wrong..
                                        </div>`
                },
                cache: false,
                contentType: false,
                processData: false,
            })
        })
    }
})