export default function Topbar({ title }: { title: string }) {
  return <div className='border-b bg-white px-6 py-4'><h1 className='text-lg font-semibold'>{title}</h1></div>
}
