import React, { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import axios from "axios";
import { toast } from "react-hot-toast";

let audioChunks: Blob[] = [];
let mediaRecorder: MediaRecorder | null = null;

const Landing: React.FC = () => {
  const [isRecordingContinuously, setIsRecordingContinuously] = useState(false);
  const [isRecordingQuestion, setIsRecordingQuestion] = useState(false);
  const [aiResponse, setAiResponse] = useState<string | null>(null);

  const startRecording = () => {
    navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
      mediaRecorder = new MediaRecorder(stream);
      console.log("MediaRecorder state:", mediaRecorder.state); //  Check initial state

      mediaRecorder.ondataavailable = (event) => {
        console.log("Received chunk of size:", event.data.size); // Chunk size
        audioChunks.push(event.data);
      };

      mediaRecorder.start();
      console.log("MediaRecorder state after start:", mediaRecorder.state); // Check state after start
    });
  };

  const stopAndSendRecording = (endpoint: string) => {
    if (mediaRecorder) {
      mediaRecorder.onstop = () => {
        const sendSavedRecording = async () => {
          console.log("MediaRecorder MimeType:", mediaRecorder?.mimeType); // Add this debug log

          const audioBlob = new Blob(audioChunks, { type: "audio/mp3" });
          console.log("Created Blob of size:", audioBlob.size); // Debug 5: Blob size

          const formData = new FormData();
          formData.append("audio", audioBlob);

          const response = await axios.post(
            `http://localhost:8000/${endpoint}`,
            formData,
            {
              headers: { "Content-Type": "multipart/form-data" },
            }
          );

          setAiResponse(response.data["text"]);
          audioChunks = [];
        };
        sendSavedRecording();
      };

      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach((track) => track.stop());
    }
  };

  const toggleContinuousRecording = () => {
    if (!isRecordingContinuously) {
      startRecording();
      toast("Audio is now being recorded continuously.");
    } else {
      stopAndSendRecording("continuous_audio");
      toast("Audio recording has stopped.");
      //stopAndSaveRecordingLocally();
    }
    setIsRecordingContinuously(!isRecordingContinuously);
  };

  const toggleQuestionRecording = () => {
    if (!isRecordingQuestion) {
      startRecording();
      toast("The question is now being recorded.");
    } else {
      stopAndSendRecording("question_audio");
      toast("The question has been recorded.");
    }
    setIsRecordingQuestion(!isRecordingQuestion);
  };

  useEffect(() => {
    const playAudio = async () => {
      const audioResponse = await axios.get("http://localhost:8000/playback", {
        responseType: "arraybuffer",
      });
      const audioData = new Blob([audioResponse.data], { type: "audio/mp3" });
      const audioUrl = URL.createObjectURL(audioData);
      const audio = new Audio(audioUrl);
      audio.play();
    };

    if (aiResponse && !isRecordingQuestion) {
      playAudio();
    }
  }, [aiResponse, isRecordingQuestion]);

  return (
    <section className="w-full h-full flex flex-col justify-center items-center">
      <div className="mt-72 w-full h-full flex flex-col justify-center items-center gap-4">
        <img src="ear.png" alt="logo" className="h-24" />
        <h1 className="text-3xl font-bold mb-12">ActivEar</h1>
        <Button
          variant={isRecordingContinuously ? "destructive" : "outline"}
          onClick={toggleContinuousRecording}
          size={"lg"}
          className="text-lg"
          disabled={isRecordingQuestion} // Disable this button if isRecordingQuestion is true
        >
          {isRecordingContinuously
            ? "Stop Continuous Recording"
            : "Start Continuous Recording"}
        </Button>
        <Button
          variant={isRecordingQuestion ? "destructive" : "outline"}
          onClick={toggleQuestionRecording}
          size={"lg"}
          className="text-lg"
          disabled={isRecordingContinuously} // Disable this button if isRecordingContinuously is true
        >
          {isRecordingQuestion ? "Stop Recording Question" : "Record Question"}
        </Button>
      </div>
      {aiResponse && (
        <div className="text-left max-w-screen-lg font-bold text-xl mt-8">
          <h3>AI Response:</h3>
          <p>{aiResponse}</p>
        </div>
      )}
    </section>
  );
};

export default Landing;
