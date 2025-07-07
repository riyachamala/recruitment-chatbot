import Chat from "../components/Chat";

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-white flex items-center justify-center p-6">
      <div className="w-full max-w-4xl bg-white shadow-xl rounded-3xl p-6 sm:p-10">
        <Chat />
      </div>
    </main>
  );
}
