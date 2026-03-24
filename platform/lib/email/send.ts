import { Resend } from 'resend';

const resend = process.env.RESEND_API_KEY
  ? new Resend(process.env.RESEND_API_KEY)
  : null;

// Use Resend verified domain, or fallback to onboarding address
const FROM_EMAIL = process.env.RESEND_FROM_EMAIL || 'SOS <onboarding@resend.dev>';

export async function sendMagicLinkEmail(to: string, magicUrl: string): Promise<boolean> {
  if (!resend) {
    console.log(`[email] No RESEND_API_KEY — skipping email to ${to}`);
    console.log(`[email] Magic link: ${magicUrl}`);
    return false;
  }

  try {
    await resend.emails.send({
      from: FROM_EMAIL,
      to,
      subject: 'Gies AI Strategy — join the deliberation',
      html: `
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 500px; margin: 0 auto; padding: 40px 20px;">
          <h1 style="color: #1a1a1a; font-size: 22px; margin-bottom: 16px;">Gies AI Strategic Operating System</h1>
          <p style="color: #555; font-size: 15px; line-height: 1.6;">
            12 AI research agents have analyzed Gies's AI strategy from six analytical lenses.
            Your expertise is needed to challenge their findings and shape the strategy.
          </p>
          <a href="${magicUrl}" style="display: inline-block; background: #ea580c; color: white; padding: 12px 28px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 15px; margin: 20px 0;">
            Enter the Deliberation
          </a>
          <p style="color: #999; font-size: 13px; margin-top: 24px;">
            This link expires in 1 hour. If you didn't request this, you can ignore this email.
          </p>
          <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;" />
          <p style="color: #bbb; font-size: 12px;">
            Gies College of Business, University of Illinois
          </p>
        </div>
      `,
    });
    console.log(`[email] Magic link sent to ${to}`);
    return true;
  } catch (error) {
    console.error(`[email] Failed to send to ${to}:`, error);
    return false;
  }
}

export async function sendAgentResponseEmail(
  to: string,
  agentName: string,
  postTitle: string,
  replyContent: string,
  postUrl: string,
): Promise<boolean> {
  if (!resend) {
    console.log(`[email] No RESEND_API_KEY — skipping agent response email to ${to}`);
    return false;
  }

  try {
    await resend.emails.send({
      from: FROM_EMAIL,
      to,
      subject: `${agentName} responded to your challenge`,
      html: `
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 500px; margin: 0 auto; padding: 40px 20px;">
          <p style="color: #555; font-size: 14px; margin-bottom: 4px;">Re: ${postTitle}</p>
          <h1 style="color: #1a1a1a; font-size: 18px; margin-bottom: 16px;">${agentName} responded to your challenge</h1>
          <div style="background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; margin-bottom: 20px;">
            <p style="color: #374151; font-size: 14px; line-height: 1.6; white-space: pre-line; margin: 0;">${replyContent.slice(0, 800)}${replyContent.length > 800 ? '...' : ''}</p>
          </div>
          <a href="${postUrl}" style="display: inline-block; background: #ea580c; color: white; padding: 10px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px;">
            Continue the debate
          </a>
          <hr style="border: none; border-top: 1px solid #eee; margin: 24px 0;" />
          <p style="color: #bbb; font-size: 12px;">
            Gies College of Business · <a href="${postUrl.split('/sos')[0]}/sos" style="color: #bbb;">Gies AI SOS</a>
          </p>
        </div>
      `,
    });
    console.log(`[email] Agent response notification sent to ${to}`);
    return true;
  } catch (error) {
    console.error(`[email] Failed to send agent response email to ${to}:`, error);
    return false;
  }
}
