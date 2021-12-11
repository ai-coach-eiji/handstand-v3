window.addEventListener("load" , function (){ 
    
    //#videoを{}内の設定で初期化、返り値のオブジェクトをplayerとする。
    let player  = videojs('video', {

        //コントローラ表示、アクセスしたら自動再生、事前ロードする(一部ブラウザではできない)
        controls: true,
        autoplay: false,
        preload: 'auto',

        fill:false,
        responsive: true,

        //再生速度の設定
        playbackRates: [ 0.25, 0.5, 1, 1.5, 2],

        //ローディングの表示
        LoadingSpinner: true,

        //音量は縦に表示
        controlBar: {
            volumePanel: { inline: false },
        }
    });

});