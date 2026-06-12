import Link from "next/link";
import Image from "next/image";

export default function HeroSection() {
  return (
    <section className="pb-4 pt-12 sm:pt-14 lg:pt-20 bg-cyan-500">
      <div className="mx-auto lg:max-w-7xl w-full px-5 sm:px-10 md:px-12 lg:px-5 grid lg:grid-cols-2 lg:items-center gap-10">
        <div className="flex flex-col space-y-8 sm:space-y-10 lg:items-center text-center lg:text-left max-w-2xl md:max-w-3xl mx-auto">
          <h1 className="font-semibold leading-tight text-teal-950 dark:text-white text-4xl sm:text-5xl lg:text-6xl">
            Revolutionizing Telehealth
            <span className="text-transparent bg-clip-text bg-gradient-to-tr from-blue-600 to-violet-600">
              {" "}
              Services
            </span>
          </h1>
          <p className="flex text-gray-700 dark:text-gray-300 tracking-tight md:font-normal max-w-xl mx-auto lg:max-w-none">
            In an era where convenience meets innovation, CureDesk is poised to become a one-stop digital
            healthcare platform, addressing the growing need for accessible, affordable, and efficient medical care.
            Designed with empathy and powered by technology, CureDesk brings healthcare to the fingertips of users,
            empowering them to take control of their well-being like never before.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 w-full">
            <Link
              href="/symptom-analysis"
              className="px-6 items-center h-12 rounded-3xl bg-primary text-white duration-300 ease-linear flex justify-center w-full sm:w-auto"
            >
              Symptoms Analysis
            </Link>
            <Link
              href="/prescription"
              className="px-6 items-center h-12 rounded-3xl text-primary border border-gray-100 dark:border-gray-800 dark:text-white bg-gray-100 dark:bg-gray-900 duration-300 ease-linear flex justify-center w-full sm:w-auto"
            >
              Prescription Analysis
            </Link>
          </div>
        </div>
        <div className="flex aspect-square lg:aspect-auto lg:h-[35rem] relative max-w-lg mx-auto lg:max-w-none w-full">
          <div className="w-3/5 h-[80%] rounded-3xl overflow-clip border-8 border-gray-200 dark:border-gray-950 z-30">
            <Image
              src="https://media.istockphoto.com/id/1298800629/photo/portrait-of-confident-male-doctor-looking-at-camera.jpg?s=2048x2048&w=is&k=20&c=nSjOQrrbcf6w00lZk7Owo5WfHdMu_WEGuZUh119U4jA="
              alt="Portrait of a confident male doctor"
              width={1300}
              height={1300}
              className="w-full h-full object-cover z-30"
            />
          </div>
          <div className="absolute right-0 bottom-0 h-[calc(100%-50px)] w-4/5 rounded-3xl overflow-clip border-4 border-gray-200 dark:border-gray-800 z-10">
            <Image
              src="https://media.istockphoto.com/id/1349936031/photo/middle-eastern-male-doctor-pointing-finger-aside-at-copyspace-studio-shot.jpg?s=2048x2048&w=is&k=20&c=52FuCbC3Qr88nfn4sFO8z7h66OIfo_1b2zB8DLetZso="
              alt="Doctor pointing aside at copy space"
              height={1300}
              width={1300}
              className="z-10 w-full h-full object-cover"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
