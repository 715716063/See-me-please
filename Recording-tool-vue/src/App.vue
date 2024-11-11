<template>
  <div class="app">
    <h1>Video Recording</h1>
    <div class="video-container">
      <video ref="video" :class="{ 'recording-border': isRecording }" autoplay playsinline class="preview-video"></video>
      <div class="overlay">
        <video ref="camera" v-if="isCameraOn" autoplay playsinline class="camera-video"></video>
      </div>
    </div>

    <div class="controls">

      <el-button  color="#626aef" :dark="isDark" size="large" type="primary" @click="openSettings" >
        <el-icon><Setting /></el-icon>
      </el-button>

      <el-button  color="#626aef" :dark="isDark" @click="toggleCamera">{{ isCameraOn ? 'Close Camera' : 'Open Camera' }}</el-button>
      <el-button  color="#626aef" :dark="isDark" @click="startRecording" :disabled="isRecording || isPaused">Start</el-button>
      <el-button color="#626aef" :dark="isDark" @click="pauseRecording" v-if="isRecording && !isPaused">Pause</el-button>
      <el-button  color="#626aef" :dark="isDark"@click="resumeRecording" v-if="isPaused">Continue</el-button>
      <el-button color="#626aef" :dark="isDark" @click="stopAndMerge" :disabled="!isRecording">Stop</el-button>
      <el-button  color="#626aef" :dark="isDark" @click="stopAndSwitchScreen">Switch Screen</el-button>
      <el-button  color="#626aef" :dark="isDark"@click="restartRecording" v-if="!isRecording && (videoURL || audioURL)">Re-start</el-button>

      <el-button  color="#626aef" :dark="isDark" @click="uploadFile">Upload to S3</el-button>
      <a v-if="videoURL" :href="videoURL" download="combined-video.mp4">Download Video</a>
      <a v-if="audioURL" :href="audioURL" download="audio.mp3">Download Audio</a>
    </div>
    <div v-if="showSettings" class="settings-form">
      <el-form :model="settingsForm">
        <el-form-item label="Resolution">
          <el-select v-model="settingsForm.resolution" placeholder="Choose Resolution">
            <el-option label="1280x720" value="1280x720"></el-option>
            <el-option label="1920x1080" value="1920x1080"></el-option>
            <el-option label="640x480" value="640x480"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="Time (second)">
          <el-input-number v-model="settingsForm.recordingDuration" :min="10" :max="600"></el-input-number>
        </el-form-item>
        <div class="form-buttons">
          <el-button @click="closeSettings">Cancel</el-button>
          <el-button type="primary" @click="applySettings">Apply</el-button>
        </div>
      </el-form>
    </div>
  </div>

</template>

<script>
import { Setting } from '@element-plus/icons-vue';
import AWS from 'aws-sdk';

export default {
  components: {
    Setting
  },
  data() {
    return {
      mediaRecorder: null,
      showSettings: false,
      isRecording: false,
      isPaused: false,
      isCameraOn: true,
      videoChunks: [],
      audioChunks: [],
      allVideoChunks: [],
      allAudioChunks: [],
      videoURL: null,
      audioURL: null,
      cameraStream: null,
      screenStream: null,
      micStream: null,
      settingsForm: {
        resolution: '1280x720',
        recordingDuration: 60
      },
      selectedFile: null,
      s3: new AWS.S3({
        accessKeyId: 'aws access key id',
        secretAccessKey: 'aws secret access key',
        region: 'us-east-1'
      })
    };
  },
  methods: {
    openSettings() {
      this.showSettings = true;
      console.log("setting open");
    },
    closeSettings() {
      this.showSettings = false;
    },
    applySettings() {
      this.recordingDuration = this.settingsForm.recordingDuration;
      console.log(`Resolution: ${this.settingsForm.resolution}, Duration: ${this.settingsForm.recordingDuration}`);
      this.closeSettings();
    },
    async toggleCamera() {
      this.isCameraOn = !this.isCameraOn;
      if (this.isCameraOn) {
        await this.getCameraStream();
      } else {
        this.stopCameraStream();
      }
    },
    async getCameraStream() {
      try {
        this.cameraStream = await navigator.mediaDevices.getUserMedia({
          video: true,
          audio: false
        });
        this.$refs.camera.srcObject = this.cameraStream;
      } catch (error) {
        alert("Camera access failure: " + error.message);
      }
    },
    stopCameraStream() {
      if (this.cameraStream) {
        this.cameraStream.getTracks().forEach(track => track.stop());
        this.cameraStream = null;
      }
    },
    async startRecording() {
      if (!window.confirm("Are you sure you want to start recording your screen?")) return;

      try {
        const [width, height] = this.settingsForm.resolution.split('x').map(Number);
        const audioConstraints = {
          echoCancellation: true,
          noiseSuppression: true
        };


        this.screenStream = await navigator.mediaDevices.getDisplayMedia({
          video: {width, height},
          audio: true
        });


        this.micStream = await navigator.mediaDevices.getUserMedia({
          audio: true
        });

        if (!this.screenStream || !this.micStream) {
          return;
        }

        const audioStream = new MediaStream(this.micStream.getAudioTracks());


        const videoTracks = this.isCameraOn && this.cameraStream ?
            [...this.screenStream.getVideoTracks(), ...this.cameraStream.getVideoTracks()] :
            this.screenStream.getVideoTracks();

        const videoStream = new MediaStream(videoTracks);
        this.$refs.video.srcObject = videoStream;

        this.videoRecorder = new MediaRecorder(videoStream);
        this.audioRecorder = new MediaRecorder(audioStream);
        this.isRecording = true;
        this.isPaused = false;
        this.videoChunks = [];
        this.audioChunks = [];

        this.videoRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) this.videoChunks.push(event.data);
        };
        this.audioRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            this.audioChunks.push(event.data);
          }
        };


        // 设置停止回调
        this.videoRecorder.onstop = () => {

          this.handleRecordingStop();
        };
        this.audioRecorder.onstop = () => {

          this.handleRecordingStop();
        };
        this.videoRecorder.start();
        this.audioRecorder.start();


      } catch (error) {
        alert('Screen Recording Failure: ' + error.message);
      }
    },
    pauseRecording() {
      if (this.isRecording && !this.isPaused) {
        this.videoRecorder.pause();
        this.audioRecorder.pause();
        this.isPaused = true;
      }
    },
    resumeRecording() {
      if (this.isPaused) {
        this.videoRecorder.resume();
        this.audioRecorder.resume();
        this.isPaused = false;
      }
    },
    handleRecordingStop() {
      if (this.videoChunks.length > 0 && this.audioChunks.length > 0) {
        const videoBlob = new Blob(this.videoChunks, {type: "video/mp4"});
        const audioBlob = new Blob(this.audioChunks, {type: "audio/mp3"});

        this.allVideoChunks.push(videoBlob);
        this.allAudioChunks.push(audioBlob);


        this.videoURL = URL.createObjectURL(videoBlob);
        this.audioURL = URL.createObjectURL(audioBlob);


        this.videoChunks = [];
        this.audioChunks = [];

      }

      this.isRecording = false;
      this.isPaused = false;
    },

    stopRecording() {
      return new Promise((resolve) => {
        if (this.isRecording) {
          const videoPromise = new Promise((videoResolve) => {
            this.videoRecorder.onstop = () => {

              if (this.videoChunks.length > 0) {
                const videoBlob = new Blob(this.videoChunks, {type: "video/mp4"});
                this.allVideoChunks.push(videoBlob);
                this.videoURL = URL.createObjectURL(videoBlob);
              }
              videoResolve();
            };
            this.videoRecorder.stop();
          });

          const audioPromise = new Promise((audioResolve) => {
            this.audioRecorder.onstop = () => {

              if (this.audioChunks.length > 0) {
                const audioBlob = new Blob(this.audioChunks, {type: "audio/mp3"});
                this.allAudioChunks.push(audioBlob);
                this.audioURL = URL.createObjectURL(audioBlob);

              } else {

              }
              audioResolve();
            };
            this.audioRecorder.stop();
          });


          Promise.all([videoPromise, audioPromise]).then(() => {

            if (this.screenStream) {
              this.screenStream.getTracks().forEach(track => track.stop());
            }
            if (this.micStream) {
              this.micStream.getTracks().forEach(track => track.stop());
            }
            this.isRecording = false;
            resolve();
          });
        } else {
          resolve();
        }
      });
    },

    async stopAndMerge() {
      if (this.isRecording) {
        await this.stopRecording();
        this.mergeVideos();
        this.mergeAudios();

      }
    },


    restartRecording() {
      this.videoURL = null;
      this.audioURL = null;
      this.startRecording();
    },
    mergeVideos() {
      if (this.allVideoChunks.length === 0) return;


      const finalVideoBlob = new Blob(this.allVideoChunks, {type: "video/mp4"});
      this.videoURL = URL.createObjectURL(finalVideoBlob);


      this.allVideoChunks = [];
      alert("All video clips have been merged and the final video can be downloaded.");
    },

    mergeAudios() {
      if (this.allAudioChunks.length === 0) {

        return;
      }


      const finalAudioBlob = new Blob(this.allAudioChunks, {type: "audio/mp3"});
      this.audioURL = URL.createObjectURL(finalAudioBlob);


      this.allAudioChunks = [];
      alert("All audio clips have been merged and the final audio can be downloaded.");
    },

    async stopAndSwitchScreen() {
      if (this.isRecording) {
        await this.stopRecording();
        await this.$nextTick();
        this.startRecording();
      }
    },

    handleFileUpload(event) {
      this.selectedFile = event.target.files[0];
    },
    async uploadFile() {
      if (!this.videoURL || !this.audioURL) {
        console.log('Missing video or audio URL');
        alert('No video or audio available to upload');
        return;
      }


      const s3 = new AWS.S3({
        accessKeyId: 'aws access key id',
        secretAccessKey: 'aws secret access key id',
        region: 'us-east-1',
      });

      try {

        const videoResponse = await fetch(this.videoURL);
        const videoBlob = await videoResponse.blob();

        const videoParams = {
          Bucket: 'shuaidengtest',
          Key: 'recorded-video.mp4',
          Body: videoBlob,
          ContentType: 'video/mp4',
        };

        s3.upload(videoParams, (err, data) => {
          if (err) {
            console.log('Error uploading video:', err);
          } else {
            console.log('Video uploaded successfully', data.Location);
          }
        });


        const audioResponse = await fetch(this.audioURL);
        const audioBlob = await audioResponse.blob();

        const audioParams = {
          Bucket: 'shuaidengtest',
          Key: 'recorded-audio.mp3',
          Body: audioBlob,
          ContentType: 'audio/mp3',
        };

        s3.upload(audioParams, (err, data) => {
          if (err) {
            console.log('Error uploading audio:', err);
          } else {
            console.log('Audio uploaded successfully', data.Location);
          }
        });
      } catch (error) {
        console.error('Error fetching blobs from URLs:', error);
      }
    },
    mounted() {
      this.getCameraStream();
    }
  }
}
</script>

<style>
.app {
  text-align: center;
  margin-top: 50px;
}
.video-container {
  position: relative;
  margin-bottom: 20px;
}
.preview-video {
  width: 80%;
  height: auto;
  border: 2px solid #000;
}
.camera-video {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 160px; /* 小框框的宽度 */
  height: 120px; /* 小框框的高度 */
  border: 2px solid red; /* 框框颜色 */
}
.controls {
  margin-top: 20px;
}
button {
  padding: 10px 20px;
  margin: 0 10px;
  font-size: 16px;
}
a {
  display: inline-block;
  margin-top: 20px;
  font-size: 16px;
  color: #42b983;
  text-decoration: none;
}

/* 设置表单样式 */
.settings-form {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: white;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  border-radius: 10px;
}

.form-buttons {
  text-align: right;
  margin-top: 10px;
}

.form-buttons .el-button {
  margin-left: 10px;
}

.recording-border {
  border: 5px solid red; /* 录制时的红色边框 */
}
</style>
