"use client";
import { useState, useEffect } from "react";

export default function Page() {
  const [posts, setPosts] = useState([]);
  const [numOfForm, setNumOfForm] = useState(1);
  const [inputs, setInputs] = useState([""]);
  const [message, setMessage] = useState("");

  // データ取得
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_HOST}/scan_times`);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        setPosts(data);
      } catch (error) {
        console.error("Fetch error:", error);
      }
    };
  
    fetchData();
  }, []);

  const addAnswer = () => {
    if (numOfForm > 4) {
      console.log("これ以上増やせません");
    } else {
      setNumOfForm((prev) => prev + 1);
      setInputs((prev) => [...prev, ""]); // 空の入力欄を追加
    }
  };

  const deleteAnswer = () => {
    if (numOfForm > 1) {
      setNumOfForm((prev) => prev - 1);
      setInputs((prev) => prev.slice(0, -1)); // 最後の要素を削除
    } else {
      console.log("これ以上回答は削除できません");
    }
  };

  const handleInputChange = (index: number, value: string) => {
    setInputs((prev) => {
      const newInputs = [...prev];
      newInputs[index] = value;
      return newInputs;
    });
  };

  const handleSubmit = async () => {
    setMessage(""); // メッセージをリセット
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_HOST}/scan_times`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ scan_times: inputs }),
      });

      if (response.ok) {
        setMessage("登録が完了しました！");
      } else {
        setMessage("エラーが発生しました");
      }
    } catch (error) {
      setMessage("通信エラー");
    }
  };

  console.log(posts);
  return (
    <div className="mx-auto max-w-sm rounded-xl bg-white p-6 shadow-lg outline outline-black/5 dark:bg-slate-800 dark:shadow-none dark:-outline-offset-1 dark:outline-white/10 m-6">
      <h1 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Scan Times</h1>
      
      <div className="mb-4">
        {posts.length > 0 ? (
          posts.map((post, index) => (
            <p key={index} className="text-gray-700 dark:text-gray-300">{post.scan_time}</p>
          ))
        ) : (
          <p className="text-gray-500 dark:text-gray-400">データなし</p>
        )}
      </div>
  
      <div className="flex flex-col gap-2 mb-4">
        {inputs.map((value, i) => (
          <input
            type="time"
            key={i}
            value={value}
            required
            onChange={(e) => handleInputChange(i, e.target.value)}
            step="300"
            className="w-full rounded-md border border-gray-300 p-2 text-gray-800 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        ))}
      </div>
  
      <div className="flex space-x-2">
        <button
          className="h-8 w-8 flex items-center justify-center rounded-full bg-neutral-950 text-white text-lg transition active:scale-110 hover:bg-neutral-800"
          onClick={addAnswer}
        >
          + 
        </button>
        <button
          className="h-8 w-8 flex items-center justify-center rounded-full bg-red-600 text-white text-lg transition active:scale-110 hover:bg-red-500"
          onClick={deleteAnswer}
        >
          - 
        </button>
        <button
          className="mt-4 w-full rounded-md bg-blue-600 p-2 text-white transition active:scale-95 hover:bg-blue-500"
          onClick={handleSubmit}
        >
          送信
        </button>
      </div>
    </div>
  );
}