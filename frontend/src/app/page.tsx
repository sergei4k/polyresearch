import { ChatComponent } from "@/components/chat-component";

export default function Home() {
  return (
    <main className="flex h-screen w-full flex-col overflow-hidden bg-background text-foreground md:flex-row">
      {/* Left Panel - 2/3 width on desktop */}
      <div className="flex w-full flex-col border-b border-border md:h-full md:w-2/3 md:border-b-0 md:border-r">
        <div className="flex h-full w-full items-center justify-center p-4">
          Content
        </div>
      </div>

      {/* Right Panel - 1/3 width on desktop */}
      <div className="flex w-full flex-col md:h-full md:w-1/3">
        <ChatComponent />
      </div>
    </main>
  );
}
