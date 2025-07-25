#define SDL_MAIN_USE_CALLBACKS
#include <SDL3/SDL_main.h>
#include <SDL3/SDL.h>

#include "imgui.h"
#include "backends/imgui_impl_sdl3.h"
#include "backends/imgui_impl_sdlrenderer3.h"

struct AppState
{
  SDL_Window* window{};
  SDL_Renderer* renderer{};
  SDL_Surface surface{};
  int counter{};
};

// Called once when the app starts
SDL_AppResult SDL_AppInit(void** appstate, int argc, char* argv[])
{

  *appstate = new AppState;
  AppState& state = *static_cast<AppState*>(*appstate);
  
  if (SDL_Init(SDL_INIT_VIDEO) == false) {
    SDL_Log("Failed to init SDL: %s", SDL_GetError());
    return SDL_APP_FAILURE;
  }

    
  SDL_CreateWindowAndRenderer("imgui sdl3 hello",
			      640,
			      480,
			      SDL_WINDOW_RESIZABLE,
			      &state.window,
			      &state.renderer);


    
  IMGUI_CHECKVERSION();
  ImGui::CreateContext();
  ImGui::StyleColorsDark();

  ImGui_ImplSDL3_InitForSDLRenderer(state.window, state.renderer);
  ImGui_ImplSDLRenderer3_Init(state.renderer);

  return SDL_APP_CONTINUE;
}

SDL_AppResult SDL_AppEvent(void* appstate, SDL_Event* event)
{
  if(event->type == SDL_EVENT_QUIT)
    {
      return SDL_APP_SUCCESS;
    }
  return SDL_APP_CONTINUE;
}

// Called every frame
SDL_AppResult SDL_AppIterate(void* appstate)
{
  SDL_Event event;
  while (SDL_PollEvent(&event)) {
    if (event.type == SDL_EVENT_QUIT)
      {
	return SDL_APP_SUCCESS;
      }
    ImGui_ImplSDL3_ProcessEvent(&event);
  }

  AppState& state = *static_cast<AppState*>(appstate);
  SDL_SetRenderDrawColor(state.renderer, 20, 20, 20, 255);
  SDL_RenderClear(state.renderer);
 
  ImGui_ImplSDLRenderer3_NewFrame();
  ImGui_ImplSDL3_NewFrame();
  ImGui::NewFrame();

  ImGui::Begin("Hello");
  ImGui::Text("Counter = %d", state.counter);
  if (ImGui::Button("Click Me!")) {
    state.counter++;
  }
  ImGui::End();

  ImGui::Render();
    
  //SDL_SetRenderDrawColor(state.renderer, 20, 20, 20, 255);
  //SDL_RenderClear(state.renderer);
    
  ImGui_ImplSDLRenderer3_RenderDrawData(ImGui::GetDrawData(), state.renderer);
  //SDL_RenderPresent(state.renderer);

  SDL_Delay(16); // 60fps delay?
  SDL_RenderPresent(state.renderer);

  return SDL_APP_CONTINUE;
}

// Called when the app quits
void SDL_AppQuit(void* appstate, SDL_AppResult result) {
 
  AppState& state = *static_cast<AppState*>(appstate);
  ImGui_ImplSDLRenderer3_Shutdown();
  ImGui_ImplSDL3_Shutdown();
  ImGui::DestroyContext();

  SDL_DestroyRenderer(state.renderer);
  SDL_DestroyWindow(state.window);
  SDL_Quit();
}


