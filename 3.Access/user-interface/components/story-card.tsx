import type { Story } from "@/types/mission"

interface StoryCardProps {
  story: Story
}

export function StoryCard({ story }: StoryCardProps) {
  const formatText = (text: string) => text || ""

  return (
    <a
      href={story.url}
      target="_blank"
      className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow overflow-hidden"
    >
      {story.storyImageUrl && (
        <img
          src={story.storyImageUrl}
          alt={story.title}
          className="w-full h-40 object-cover"
        />
      )}
      <div className="p-4">
        <h4 className="text-md font-semibold text-gray-900 line-clamp-2 mb-2">
          {story.title}
        </h4>
        {story.type && (
          <span className="inline-block px-2 py-1 text-xs font-medium bg-indigo-100 text-indigo-800 rounded-full">
            {story.type}
          </span>
        )}
       
      </div>
    </a>
  )
}
