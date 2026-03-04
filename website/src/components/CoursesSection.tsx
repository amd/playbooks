import Link from "next/link";

interface Course {
  title: string;
  description: string;
  partner: string;
  href: string;
}

const courses: Course[] = [
  {
    title: "Supercharging Hugging Face LLMs on AMD",
    description:
      "Master LLM optimization and deployment on AMD hardware with official Hugging Face certification",
    partner: "Hugging Face Partnership",
    href: "/halo/huggingface-course",
  },
];

export default function CoursesSection() {
  return (
    <section className="py-12 px-6 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-[#0d0d0d] via-[#1a0f0a] to-[#0d0d0d]" />
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[#D4915D]/30 to-transparent" />

      <div className="max-w-[1400px] mx-auto relative z-10">
        <div className="flex items-center gap-2.5 mb-4">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-yellow-500/20 to-amber-500/20 border border-yellow-500/30 flex items-center justify-center">
            <svg
              className="w-4 h-4 text-yellow-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5"
              />
            </svg>
          </div>
          <div>
            <h3 className="text-base font-semibold text-white">
              Courses & Certifications
            </h3>
            <p className="text-xs text-[#6b6b6b]">
              Official learning paths with industry partners
            </p>
          </div>
        </div>

        {courses.map((course) => (
          <Link key={course.title} href={course.href} className="block group">
            <div className="bg-gradient-to-r from-[#1e1e1e] to-[#242424] border border-yellow-500/20 rounded-lg p-4 hover:border-yellow-500/40 transition-all">
              <div className="flex flex-col md:flex-row md:items-center gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1.5">
                    <span className="px-2 py-0.5 bg-yellow-500/10 text-yellow-400 text-[10px] font-semibold rounded-full border border-yellow-500/20">
                      {course.partner}
                    </span>
                  </div>
                  <h4 className="text-sm font-semibold text-white mb-1 group-hover:text-yellow-400 transition-colors">
                    {course.title}
                  </h4>
                  <p className="text-xs text-[#a0a0a0]">
                    {course.description}
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="hidden md:flex items-center gap-2 text-yellow-400 text-sm font-medium group-hover:gap-3 transition-all">
                    <span>Enroll Now</span>
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M17 8l4 4m0 0l-4 4m4-4H3"
                      />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
