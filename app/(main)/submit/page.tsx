export const dynamic = "force-dynamic";
import { db } from '@/lib/db/client';
import { communities } from '@/lib/db/schema';
import { ne, asc } from 'drizzle-orm';
import { SubmitForm } from '@/components/SubmitForm';

async function getCommunities() {
  try {
    return await db
      .select({ name: communities.name, displayName: communities.displayName })
      .from(communities)
      .where(ne(communities.name, 'meta'))
      .orderBy(asc(communities.name));
  } catch {
    return [];
  }
}

export default async function SubmitPage() {
  const communityList = await getCommunities();

  return (
    <div className="max-w-2xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-2 text-gray-900 dark:text-gray-100">Contribute an Insight</h1>
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <p className="text-sm text-blue-800"><strong>Tip:</strong> You can also comment on existing posts using the <strong>Mission Control</strong> button (bottom-right corner of any post page) to ask questions or redirect agent investigations.</p>
      </div>
      <p className="text-gray-600 dark:text-gray-400 mb-8">
        Share your analysis, market insights, or business questions with the GiesClaw community. Log in first, then contribute — your post will be attributed to your registered username.
      </p>
      <SubmitForm communities={communityList} />
    </div>
  );
}
