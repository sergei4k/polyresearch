import { ChatComponent } from "@/components/chat-component";

export default function Home() {
  return (
    <main className="flex h-screen w-full flex-col overflow-hidden bg-background text-foreground md:flex-row">
      {/* Far Left Sidebar - 50px width */}
      <div className="flex h-[50px] w-full flex-none items-center justify-center border-b border-border md:h-full md:w-[50px] md:flex-col md:border-b-0 md:border-r">
        {/* Sidebar content (icons etc) can go here */}
      </div>

      {/* Left Panel - 2/3 width on desktop (remaining width) */}
      <div className="flex w-full flex-1 flex-col border-b border-border md:h-full md:border-b-0 md:border-r">
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
